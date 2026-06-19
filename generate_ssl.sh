#!/bin/bash
# ============================================================
# Script para generar certificado SSL auto-firmado
# para las IPs del servidor: 10.10.0.56, 10.10.0.57, 10.10.0.58
# ============================================================

set -e

CERT_DIR="./nginx/certs"
mkdir -p "$CERT_DIR"

echo "🔐 Generando certificado SSL auto-firmado para las IPs:"
echo "   📍 10.10.0.56"
echo "   📍 10.10.0.57"
echo "   📍 10.10.0.58"
echo ""

# Crear archivo de configuración con extensión SAN (Subject Alternative Name)
# Necesario para que Chrome/Firefox acepten el certificado por IP
cat > /tmp/openssl_san.cnf <<EOF
[req]
default_bits       = 2048
prompt             = no
default_md         = sha256
distinguished_name = dn
req_extensions     = v3_req
x509_extensions    = v3_ca

[dn]
C=MX
ST=Puebla
L=Oriental
O=UT de Oriental
OU=Bolsa de Trabajo
CN=10.10.0.57

[v3_req]
subjectAltName = @alt_names

[v3_ca]
subjectAltName = @alt_names
basicConstraints = critical, CA:false
keyUsage = critical, digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth

[alt_names]
IP.1 = 10.10.0.56
IP.2 = 10.10.0.57
IP.3 = 10.10.0.58
IP.4 = 127.0.0.1
EOF

# Generar la clave privada y el certificado auto-firmado (válido 3 años)
openssl req -x509 -nodes -days 1095 \
  -newkey rsa:2048 \
  -keyout "$CERT_DIR/cert.key" \
  -out "$CERT_DIR/cert.crt" \
  -config /tmp/openssl_san.cnf

echo ""
echo "✅ Certificado generado exitosamente en: $CERT_DIR"
echo "   📄 Certificado: $CERT_DIR/cert.crt"
echo "   🔑 Llave privada: $CERT_DIR/cert.key"
echo ""
echo "🔍 Verificando las IPs incluidas en el certificado:"
openssl x509 -in "$CERT_DIR/cert.crt" -noout -ext subjectAltName
echo ""
echo "🚀 Ahora ejecuta: sudo docker compose up -d --build"
