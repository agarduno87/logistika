<?php
/**
 * logistika — recepción de leads por correo (Neubox / cPanel, sin base de datos).
 * Reemplaza al backend FastAPI en producción. Recibe el POST del formulario,
 * valida, y envía el lead por correo. No guarda nada en disco.
 *
 * ── PENDIENTE DE CONFIRMAR MAÑANA (marcados con TODO) ──────────────────────
 *   TODO(correo): dirección real que recibe los leads.
 *   TODO(dominio): remitente en el mismo dominio del sitio para no caer en spam.
 * ───────────────────────────────────────────────────────────────────────────
 */

// === CONFIG (confirmar) ======================================================
const LEAD_TO   = 'hola@logistika.com.mx';                 // TODO(correo): ¿.mx o .com.mx?
const LEAD_FROM = 'no-reply@logistika.mx';                 // TODO(dominio): buzón/alias real en Neubox
const SITE_NAME = 'logistika';
$ALLOWED_STAGES = ['Already importing','Want to start','Specific problem','Outsource'];
$ALLOWED_LOCALES = ['en','es'];
// ============================================================================

header('Content-Type: application/json; charset=utf-8');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['detail' => 'Method not allowed']); exit;
}

// Acepta JSON (fetch actual) o form-urlencoded.
$raw = file_get_contents('php://input');
$data = json_decode($raw, true);
if (!is_array($data)) { $data = $_POST; }

$company = trim($data['company'] ?? '');
$email   = trim($data['email'] ?? '');
$stage   = trim($data['stage'] ?? '');
$message = trim($data['message'] ?? '');
$locale  = trim($data['locale'] ?? 'es');
$website = trim($data['website'] ?? '');   // honeypot anti-bots (debe venir vacío)

// Honeypot: si viene lleno, fingimos éxito y descartamos.
if ($website !== '') { echo json_encode(['status' => 'ok']); exit; }

$errors = [];
if ($company === '' || mb_strlen($company) > 200) $errors[] = 'company';
if (!filter_var($email, FILTER_VALIDATE_EMAIL))   $errors[] = 'email';
if (!in_array($stage, $ALLOWED_STAGES, true))      $errors[] = 'stage';
if (mb_strlen($message) > 4000)                    $errors[] = 'message';
if (!in_array($locale, $ALLOWED_LOCALES, true))    $locale = 'es';

if ($errors) {
    http_response_code(422);
    echo json_encode(['detail' => 'validation error', 'fields' => $errors]); exit;
}

// Construye el correo.
$subject = "[{$SITE_NAME}] {$stage} — {$company}";
$body  = "Nuevo lead desde el sitio\n";
$body .= "───────────────────────────\n";
$body .= "Empresa:  {$company}\n";
$body .= "Correo:   {$email}\n";
$body .= "Momento:  {$stage}\n";
$body .= "Idioma:   {$locale}\n";
$body .= "Mensaje:\n{$message}\n";
$body .= "───────────────────────────\n";
$body .= "Fecha: " . date('Y-m-d H:i:s') . "\n";

$headers  = "From: {$SITE_NAME} <" . LEAD_FROM . ">\r\n";
$headers .= "Reply-To: {$email}\r\n";
$headers .= "Content-Type: text/plain; charset=utf-8\r\n";

$sent = @mail(LEAD_TO, '=?UTF-8?B?' . base64_encode($subject) . '?=', $body, $headers);

if (!$sent) {
    http_response_code(502);
    echo json_encode(['detail' => 'mail failed']); exit;
}

echo json_encode(['status' => 'ok']);
