#!/usr/bin/env bash
# RootCause check: all DDNS records must match the current public IP.
# Exits 0 (OK) or 1 with a description of each mismatch.

DOMAINS=(
    "rootcause.example.com"
    "rootcause.example.com"
)

PUBLIC_IP=""
for provider in "https://api.ipify.org" "https://ifconfig.me" "https://icanhazip.com"; do
    ip=$(curl -fsS -m 5 "$provider" 2>/dev/null | tr -d '[:space:]')
    if [[ "$ip" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        PUBLIC_IP="$ip"
        break
    fi
done

if [[ -z "$PUBLIC_IP" ]]; then
    echo "Cannot determine public IP — all providers unreachable"
    exit 1
fi

ERRORS=()
for DOMAIN in "${DOMAINS[@]}"; do
    DNS_IP=$(getent hosts "$DOMAIN" 2>/dev/null | awk '{print $1}' \
             | grep -E '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$' | head -1)
    if [[ -z "$DNS_IP" ]]; then
        ERRORS+=("$DOMAIN: DNS not resolving")
    elif [[ "$DNS_IP" != "$PUBLIC_IP" ]]; then
        ERRORS+=("$DOMAIN: DNS=$DNS_IP expected=$PUBLIC_IP")
    fi
done

if [[ ${#ERRORS[@]} -gt 0 ]]; then
    printf "DDNS mismatch (public IP: %s):\n" "$PUBLIC_IP"
    for err in "${ERRORS[@]}"; do
        printf "  - %s\n" "$err"
    done
    exit 1
fi

echo "All DDNS records up to date ($PUBLIC_IP)"
