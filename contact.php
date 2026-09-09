<?php
/**
 * logistika — recepción de leads por correo (Neubox / cPanel, sin base de datos).
 * Reemplaza al backend FastAPI en producción, con la MISMA defensa en profundidad:
 *   honeypot + trampa de tiempo + rate limit + validación + CORS cerrado
 *   + secretos por entorno + logging anonimizado (sin cuerpo, sin correo completo).
 *
 * ── CONFIG POR ENTORNO (cPanel: SetEnv en .htaccess, o edita los defaults) ──
 *   LEAD_TO, LEAD_FROM, ALLOWED_ORIGIN, RATE_LIMIT_MAX, RATE_LIMIT_WINDOW_SECONDS
 *   TODO(confirmar mañana): LEAD_TO real y dominio del remitente.
 * ───────────────────────────────────────────────────────────────────────────
 */

// === CONFIG (por entorno, con defaults) ======================================
$LEAD_TO   = getenv('LEAD_TO')   ?: 'hola@logistika.com.mx';   // TODO(correo)
$LEAD_FROM = getenv('LEAD_FROM') ?: 'no-reply@logistika.mx';   // TODO(dominio)
$ALLOWED_ORIGIN = getenv('ALLOWED_ORIGIN') ?: 'https://www.logistika.mx';
$RATE_LIMIT_MAX = (int)(getenv('RATE_LIMIT_MAX') ?: 5);
$RATE_LIMIT_WINDOW = (int)(getenv('RATE_LIMIT_WINDOW_SECONDS') ?: 3600);

$SITE_NAME       = 'logistika';
$MIN_FILL_SECONDS = 3;
$MAX_BODY_BYTES   = 16 * 1024;
$ALLOWED_STAGES   = ['Already importing','Want to start','Specific problem','Outsource'];
$ALLOWED_LOCALES  = ['en','es'];
// ============================================================================

// --- CORS cerrado a un solo origen (nunca *) --------------------------------
header('Vary: Origin');
$origin = $_SERVER['HTTP_ORIGIN'] ?? '';
if ($origin === $ALLOWED_ORIGIN) {
    header("Access-Control-Allow-Origin: {$ALLOWED_ORIGIN}");
    header('Access-Control-Allow-Methods: POST');
    header('Access-Control-Allow-Headers: Content-Type, Accept');
    header('Access-Control-Max-Age: 600');
}
header('Content-Type: application/json; charset=utf-8');

if (($_SERVER['REQUEST_METHOD'] ?? '') === 'OPTIONS') { http_response_code(204); exit; }
if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    http_response_code(405); echo json_encode(['detail' => 'Method not allowed']); exit;
}

// --- IP + anonimizado (logs sin PII completa) -------------------------------
function client_ip(): string {
    $fwd = $_SERVER['HTTP_X_FORWARDED_FOR'] ?? '';
    if ($fwd !== '') return trim(explode(',', $fwd)[0]);
    return $_SERVER['REMOTE_ADDR'] ?? 'unknown';
}
function anonymise(string $ip): string {
    if (strpos($ip, ':') !== false) {           // IPv6 -> /48
        return implode(':', array_slice(explode(':', $ip), 0, 3)) . '::/48';
    }
    $p = explode('.', $ip);                      // IPv4 -> sin último octeto
    return count($p) === 4 ? "{$p[0]}.{$p[1]}.{$p[2]}.0" : 'unknown';
}
function lead_log(string $msg): void { error_log("[logistika] {$msg}"); }

$ip = client_ip();
$anon = anonymise($ip);

// --- Rate limit por IP (archivo + flock, sin base de datos) ------------------
function rate_limited(string $ip, int $max, int $window): bool {
    $dir = sys_get_temp_dir() . '/logistika_rl';
    if (!is_dir($dir)) @mkdir($dir, 0700, true);
    $file = $dir . '/' . hash('sha256', $ip) . '.json';
    $now = time();
    $fh = @fopen($file, 'c+');
    if ($fh === false) return false;             // si no se puede escribir, no bloquea el lead
    flock($fh, LOCK_EX);
    $raw = stream_get_contents($fh);
    $hits = json_decode($raw ?: '[]', true);
    if (!is_array($hits)) $hits = [];
    $hits = array_values(array_filter($hits, fn($t) => $now - $t <= $window));
    $limited = count($hits) >= $max;
    if (!$limited) $hits[] = $now;
    ftruncate($fh, 0); rewind($fh); fwrite($fh, json_encode($hits));
    flock($fh, LOCK_UN); fclose($fh);
    return $limited;
}

// --- Cuerpo (límite de tamaño) ----------------------------------------------
$raw = file_get_contents('php://input');
if (strlen($raw) > $MAX_BODY_BYTES) {
    http_response_code(413); echo json_encode(['detail' => 'payload too large']); exit;
}
$data = json_decode($raw, true);
if (!is_array($data)) $data = $_POST;

$company = trim($data['company'] ?? '');
$email   = trim($data['email'] ?? '');
$stage   = trim($data['stage'] ?? '');
$message = trim($data['message'] ?? '');
$locale  = trim($data['locale'] ?? 'es');
$website = trim($data['website'] ?? '');                 // honeypot
$rendered_at = (int)($data['rendered_at'] ?? 0);         // trampa de tiempo (ms)

// --- Honeypot: campo oculto lleno = bot. Fingimos éxito y descartamos --------
if ($website !== '') { lead_log("honeypot triggered ip={$anon}"); echo json_encode(['status' => 'ok']); exit; }

// --- Trampa de tiempo: enviado demasiado rápido = bot ------------------------
if ($rendered_at > 0) {
    $elapsed = time() - intdiv($rendered_at, 1000);
    if ($elapsed < $MIN_FILL_SECONDS) {
        lead_log("timetrap triggered ip={$anon}");
        echo json_encode(['status' => 'ok']); exit;     // silencioso, como el honeypot
    }
}

// --- Validación (equivalente a Pydantic) ------------------------------------
$errors = [];
if ($company === '' || mb_strlen($company) > 200) $errors[] = 'company';
if (!filter_var($email, FILTER_VALIDATE_EMAIL) || mb_strlen($email) > 254) $errors[] = 'email';
if (!in_array($stage, $ALLOWED_STAGES, true))     $errors[] = 'stage';
if (mb_strlen($message) > 4000)                   $errors[] = 'message';
if (preg_match('/[\x00-\x08\x0B\x0C\x0E-\x1F]/', $company . $message)) $errors[] = 'control-chars';
if (!in_array($locale, $ALLOWED_LOCALES, true))   $locale = 'es';
if ($errors) { http_response_code(422); echo json_encode(['detail' => 'validation error', 'fields' => $errors]); exit; }

// --- Rate limit --------------------------------------------------------------
if (rate_limited($ip, $RATE_LIMIT_MAX, $RATE_LIMIT_WINDOW)) {
    lead_log("rate limited ip={$anon}");
    http_response_code(429); echo json_encode(['detail' => 'too many requests']); exit;
}

// --- Envío del correo --------------------------------------------------------
$subject = "[{$SITE_NAME}] {$stage} — {$company}";
$body  = "Nuevo lead desde el sitio\n───────────────────────────\n";
$body .= "Empresa:  {$company}\nCorreo:   {$email}\nMomento:  {$stage}\nIdioma:   {$locale}\n";
$body .= "Mensaje:\n{$message}\n───────────────────────────\nFecha: " . date('Y-m-d H:i:s') . "\n";

$headers  = "From: {$SITE_NAME} <{$LEAD_FROM}>\r\n";
$headers .= "Reply-To: {$email}\r\n";
$headers .= "Content-Type: text/plain; charset=utf-8\r\n";
$encodedSubject = '=?UTF-8?B?' . base64_encode($subject) . '?=';

$sent = @mail($LEAD_TO, $encodedSubject, $body, $headers);

// Logging anonimizado: solo dominio del correo, IP anonimizada, sin cuerpo.
$emailDomain = substr(strrchr($email, '@') ?: '@?', 1);
lead_log(($sent ? 'lead sent' : 'mail FAILED') . " stage={$stage} email_domain={$emailDomain} ip={$anon}");

if (!$sent) { http_response_code(502); echo json_encode(['detail' => 'mail failed']); exit; }
echo json_encode(['status' => 'ok']);
