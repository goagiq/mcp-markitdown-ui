#!/bin/bash

# Security Audit Script for MarkItDown with Vision OCR
# This script performs comprehensive security audits and compliance checks

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SECURITY_DIR="$PROJECT_ROOT/security"
AUDIT_DIR="$SECURITY_DIR/audit"
REPORTS_DIR="$AUDIT_DIR/reports"
SCAN_DIR="$AUDIT_DIR/scans"

# Create audit directories
mkdir -p "$REPORTS_DIR" "$SCAN_DIR"

# Function to check security dependencies
check_security_dependencies() {
    log_info "Checking security audit dependencies..."
    
    local missing_deps=()
    
    # Check for Trivy (container vulnerability scanner)
    if ! command -v trivy &> /dev/null; then
        missing_deps+=("trivy")
    fi
    
    # Check for Bandit (Python security linter)
    if ! command -v bandit &> /dev/null; then
        missing_deps+=("bandit")
    fi
    
    # Check for Safety (Python dependency vulnerability checker)
    if ! command -v safety &> /dev/null; then
        missing_deps+=("safety")
    fi
    
    # Check for Docker Bench Security
    if ! command -v docker-bench-security &> /dev/null; then
        missing_deps+=("docker-bench-security")
    fi
    
    # Check for Lynis (system security audit)
    if ! command -v lynis &> /dev/null; then
        missing_deps+=("lynis")
    fi
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        log_warning "Missing security tools: ${missing_deps[*]}"
        log_info "Installing missing dependencies..."
        
        # Install Trivy
        if [[ " ${missing_deps[*]} " =~ " trivy " ]]; then
            curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
        fi
        
        # Install Bandit
        if [[ " ${missing_deps[*]} " =~ " bandit " ]]; then
            pip install bandit
        fi
        
        # Install Safety
        if [[ " ${missing_deps[*]} " =~ " safety " ]]; then
            pip install safety
        fi
        
        # Install Docker Bench Security
        if [[ " ${missing_deps[*]} " =~ " docker-bench-security " ]]; then
            git clone https://github.com/docker/docker-bench-security.git /tmp/docker-bench-security
            sudo cp /tmp/docker-bench-security/docker-bench-security.sh /usr/local/bin/docker-bench-security
            sudo chmod +x /usr/local/bin/docker-bench-security
        fi
        
        # Install Lynis
        if [[ " ${missing_deps[*]} " =~ " lynis " ]]; then
            sudo apt-get update && sudo apt-get install -y lynis
        fi
    fi
    
    log_success "Security dependencies check completed"
}

# Function to perform container security scanning
scan_containers() {
    log_info "Performing container security scanning..."
    
    local scan_report="$SCAN_DIR/container_scan_$(date +%Y%m%d_%H%M%S).json"
    local summary_report="$REPORTS_DIR/container_security_summary.txt"
    
    # Scan all Docker images
    log_info "Scanning Docker images for vulnerabilities..."
    
    # Get list of images
    local images=$(docker images --format "{{.Repository}}:{{.Tag}}" | grep -v "<none>")
    
    if [[ -z "$images" ]]; then
        log_warning "No Docker images found to scan"
        return 0
    fi
    
    # Create scan report header
    cat > "$scan_report" << EOF
{
  "scan_date": "$(date -Iseconds)",
  "scanner": "trivy",
  "images": []
}
EOF
    
    local total_vulnerabilities=0
    local critical_vulnerabilities=0
    local high_vulnerabilities=0
    
    # Scan each image
    while IFS= read -r image; do
        log_info "Scanning image: $image"
        
        # Run Trivy scan
        local image_scan_file="/tmp/trivy_scan_$(echo "$image" | tr ':/' '_').json"
        trivy image --format json --output "$image_scan_file" "$image" || {
            log_warning "Failed to scan image: $image"
            continue
        }
        
        # Parse scan results
        local vuln_count=$(jq '.Results[].Vulnerabilities | length' "$image_scan_file" 2>/dev/null | awk '{sum+=$1} END {print sum+0}')
        local critical_count=$(jq '.Results[].Vulnerabilities[] | select(.Severity == "CRITICAL") | .VulnerabilityID' "$image_scan_file" 2>/dev/null | wc -l)
        local high_count=$(jq '.Results[].Vulnerabilities[] | select(.Severity == "HIGH") | .VulnerabilityID' "$image_scan_file" 2>/dev/null | wc -l)
        
        total_vulnerabilities=$((total_vulnerabilities + vuln_count))
        critical_vulnerabilities=$((critical_vulnerabilities + critical_count))
        high_vulnerabilities=$((high_vulnerabilities + high_count))
        
        # Add to main report
        jq --arg img "$image" --arg count "$vuln_count" --arg critical "$critical_count" --arg high "$high_count" \
           '.images += [{"image": $img, "vulnerabilities": $count, "critical": $critical, "high": $high}]' \
           "$scan_report" > "$scan_report.tmp" && mv "$scan_report.tmp" "$scan_report"
        
        # Clean up temporary file
        rm -f "$image_scan_file"
        
    done <<< "$images"
    
    # Generate summary report
    cat > "$summary_report" << EOF
Container Security Scan Summary
===============================

Scan Date: $(date)
Total Images Scanned: $(echo "$images" | wc -l)
Total Vulnerabilities: $total_vulnerabilities
Critical Vulnerabilities: $critical_vulnerabilities
High Vulnerabilities: $high_vulnerabilities

Recommendations:
$(generate_container_recommendations "$critical_vulnerabilities" "$high_vulnerabilities")

Detailed scan results available in: $scan_report
EOF
    
    if [[ $critical_vulnerabilities -gt 0 ]]; then
        log_error "Critical vulnerabilities found: $critical_vulnerabilities"
        return 1
    elif [[ $high_vulnerabilities -gt 0 ]]; then
        log_warning "High vulnerabilities found: $high_vulnerabilities"
    else
        log_success "No critical or high vulnerabilities found"
    fi
}

# Function to perform code security analysis
analyze_code_security() {
    log_info "Performing code security analysis..."
    
    local bandit_report="$SCAN_DIR/bandit_scan_$(date +%Y%m%d_%H%M%S).json"
    local safety_report="$SCAN_DIR/safety_scan_$(date +%Y%m%d_%H%M%S).json"
    local code_summary="$REPORTS_DIR/code_security_summary.txt"
    
    # Run Bandit security analysis
    log_info "Running Bandit security analysis..."
    bandit -r "$PROJECT_ROOT" -f json -o "$bandit_report" || {
        log_warning "Bandit analysis failed"
        return 1
    }
    
    # Run Safety dependency check
    log_info "Running Safety dependency vulnerability check..."
    safety check --json --output "$safety_report" || {
        log_warning "Safety check failed"
        return 1
    }
    
    # Parse results
    local bandit_issues=$(jq '.results | length' "$bandit_report" 2>/dev/null || echo "0")
    local safety_issues=$(jq '.vulnerabilities | length' "$safety_report" 2>/dev/null || echo "0")
    
    # Generate summary
    cat > "$code_summary" << EOF
Code Security Analysis Summary
==============================

Analysis Date: $(date)
Bandit Issues Found: $bandit_issues
Safety Issues Found: $safety_issues

Bandit Analysis:
$(if [[ $bandit_issues -gt 0 ]]; then
    jq -r '.results[] | "- \(.issue_text) (Severity: \(.issue_severity), Line: \(.line_number))"' "$bandit_report" 2>/dev/null || echo "No issues found"
else
    echo "No security issues found"
fi)

Safety Analysis:
$(if [[ $safety_issues -gt 0 ]]; then
    jq -r '.vulnerabilities[] | "- \(.package) \(.installed_version): \(.advisory)"' "$safety_report" 2>/dev/null || echo "No issues found"
else
    echo "No dependency vulnerabilities found"
fi)

Recommendations:
$(generate_code_recommendations "$bandit_issues" "$safety_issues")

Detailed reports available in:
- Bandit: $bandit_report
- Safety: $safety_report
EOF
    
    if [[ $bandit_issues -gt 0 ]] || [[ $safety_issues -gt 0 ]]; then
        log_warning "Code security issues found: $bandit_issues Bandit, $safety_issues Safety"
    else
        log_success "No code security issues found"
    fi
}

# Function to perform Docker security audit
audit_docker_security() {
    log_info "Performing Docker security audit..."
    
    local docker_audit_report="$SCAN_DIR/docker_audit_$(date +%Y%m%d_%H%M%S).txt"
    local docker_summary="$REPORTS_DIR/docker_security_summary.txt"
    
    # Run Docker Bench Security
    log_info "Running Docker Bench Security audit..."
    docker-bench-security > "$docker_audit_report" 2>&1 || {
        log_warning "Docker Bench Security audit failed"
        return 1
    }
    
    # Parse results
    local passed_tests=$(grep -c "PASS" "$docker_audit_report" || echo "0")
    local failed_tests=$(grep -c "WARN\|FAIL" "$docker_audit_report" || echo "0")
    
    # Generate summary
    cat > "$docker_summary" << EOF
Docker Security Audit Summary
=============================

Audit Date: $(date)
Tests Passed: $passed_tests
Tests Failed/Warned: $failed_tests

Failed/Warning Tests:
$(grep -E "(WARN|FAIL)" "$docker_audit_report" | head -10 || echo "No failed tests")

Recommendations:
$(generate_docker_recommendations "$failed_tests")

Full audit report available in: $docker_audit_report
EOF
    
    if [[ $failed_tests -gt 0 ]]; then
        log_warning "Docker security issues found: $failed_tests tests failed/warned"
    else
        log_success "Docker security audit passed"
    fi
}

# Function to perform system security audit
audit_system_security() {
    log_info "Performing system security audit..."
    
    local lynis_report="$SCAN_DIR/lynis_audit_$(date +%Y%m%d_%H%M%S).log"
    local system_summary="$REPORTS_DIR/system_security_summary.txt"
    
    # Run Lynis system audit
    log_info "Running Lynis system security audit..."
    sudo lynis audit system --quick > "$lynis_report" 2>&1 || {
        log_warning "Lynis system audit failed"
        return 1
    }
    
    # Parse results
    local warnings=$(grep -c "Warning" "$lynis_report" || echo "0")
    local suggestions=$(grep -c "Suggestion" "$lynis_report" || echo "0")
    local score=$(grep "Hardening index" "$lynis_report" | awk '{print $3}' || echo "0")
    
    # Generate summary
    cat > "$system_summary" << EOF
System Security Audit Summary
=============================

Audit Date: $(date)
Hardening Index: $score/100
Warnings: $warnings
Suggestions: $suggestions

Key Findings:
$(grep -E "(Warning|Suggestion)" "$lynis_report" | head -10 || echo "No issues found")

Recommendations:
$(generate_system_recommendations "$score" "$warnings")

Full audit report available in: $lynis_report
EOF
    
    if [[ $warnings -gt 0 ]]; then
        log_warning "System security warnings found: $warnings"
    else
        log_success "System security audit completed"
    fi
}

# Function to check network security
check_network_security() {
    log_info "Checking network security..."
    
    local network_report="$REPORTS_DIR/network_security_report.txt"
    
    cat > "$network_report" << EOF
Network Security Assessment
===========================

Assessment Date: $(date)

1. Open Ports:
$(netstat -tuln | grep LISTEN | awk '{print "   - " $4}' || echo "   No listening ports found")

2. Firewall Status:
$(if command -v ufw &> /dev/null; then
    echo "   UFW Status: $(sudo ufw status)"
else
    echo "   UFW not installed"
fi)

3. Docker Network Configuration:
$(docker network ls --format "table {{.Name}}\t{{.Driver}}\t{{.Scope}}" || echo "   No Docker networks found")

4. Container Port Mappings:
$(docker ps --format "table {{.Names}}\t{{.Ports}}" || echo "   No running containers found")

5. Security Recommendations:
$(generate_network_recommendations)
EOF
    
    log_success "Network security assessment completed"
}

# Function to check secrets and credentials
check_secrets() {
    log_info "Checking for exposed secrets and credentials..."
    
    local secrets_report="$REPORTS_DIR/secrets_scan_report.txt"
    local secrets_found=0
    
    cat > "$secrets_report" << EOF
Secrets and Credentials Scan
============================

Scan Date: $(date)

1. Environment Files:
$(find "$PROJECT_ROOT" -name "*.env*" -type f | while read -r file; do
    echo "   - $file"
    if grep -q -E "(password|secret|key|token)" "$file" 2>/dev/null; then
        echo "     WARNING: Contains potential secrets"
        secrets_found=$((secrets_found + 1))
    fi
done)

2. Configuration Files:
$(find "$PROJECT_ROOT" -name "*.conf" -o -name "*.config" -o -name "*.yml" -o -name "*.yaml" | while read -r file; do
    if grep -q -E "(password|secret|key|token)" "$file" 2>/dev/null; then
        echo "   - $file (contains potential secrets)"
        secrets_found=$((secrets_found + 1))
    fi
done)

3. Docker Compose Files:
$(find "$PROJECT_ROOT" -name "docker-compose*.yml" | while read -r file; do
    if grep -q -E "(password|secret|key|token)" "$file" 2>/dev/null; then
        echo "   - $file (contains potential secrets)"
        secrets_found=$((secrets_found + 1))
    fi
done)

4. Code Files:
$(grep -r -l -E "(password|secret|key|token)" "$PROJECT_ROOT" --include="*.py" --include="*.js" --include="*.sh" 2>/dev/null | while read -r file; do
    echo "   - $file (contains potential secrets)"
    secrets_found=$((secrets_found + 1))
done)

Total Potential Secrets Found: $secrets_found

Recommendations:
- Use environment variables for sensitive data
- Implement secrets management (HashiCorp Vault, AWS Secrets Manager)
- Use Docker secrets for containerized applications
- Regularly rotate credentials and keys
- Implement least privilege access controls
EOF
    
    if [[ $secrets_found -gt 0 ]]; then
        log_warning "Potential secrets found: $secrets_found"
    else
        log_success "No exposed secrets found"
    fi
}

# Function to generate recommendations
generate_container_recommendations() {
    local critical="$1"
    local high="$2"
    
    echo "Container Security Recommendations:"
    echo
    if [[ $critical -gt 0 ]]; then
        echo "- CRITICAL: Update base images to fix critical vulnerabilities"
        echo "- CRITICAL: Review and patch all critical security issues immediately"
    fi
    if [[ $high -gt 0 ]]; then
        echo "- HIGH: Update dependencies to fix high severity vulnerabilities"
        echo "- HIGH: Consider using multi-stage builds to reduce attack surface"
    fi
    echo "- MEDIUM: Regularly update base images and dependencies"
    echo "- MEDIUM: Use minimal base images (alpine, distroless)"
    echo "- LOW: Implement image signing and verification"
    echo "- LOW: Use non-root users in containers"
}

generate_code_recommendations() {
    local bandit_issues="$1"
    local safety_issues="$2"
    
    echo "Code Security Recommendations:"
    echo
    if [[ $bandit_issues -gt 0 ]]; then
        echo "- Review and fix Bandit security issues"
        echo "- Implement secure coding practices"
        echo "- Use security linters in CI/CD pipeline"
    fi
    if [[ $safety_issues -gt 0 ]]; then
        echo "- Update vulnerable dependencies"
        echo "- Implement automated dependency scanning"
        echo "- Use dependency pinning for reproducible builds"
    fi
    echo "- Regular security code reviews"
    echo "- Implement SAST (Static Application Security Testing)"
    echo "- Use security-focused development practices"
}

generate_docker_recommendations() {
    local failed_tests="$1"
    
    echo "Docker Security Recommendations:"
    echo
    if [[ $failed_tests -gt 0 ]]; then
        echo "- Review and fix failed Docker security tests"
        echo "- Implement Docker security best practices"
    fi
    echo "- Use Docker Content Trust for image signing"
    echo "- Implement resource limits for containers"
    echo "- Use read-only root filesystems where possible"
    echo "- Implement proper logging and monitoring"
    echo "- Regular security updates for Docker daemon"
}

generate_system_recommendations() {
    local score="$1"
    local warnings="$2"
    
    echo "System Security Recommendations:"
    echo
    if [[ $score -lt 70 ]]; then
        echo "- CRITICAL: Implement system hardening measures"
        echo "- CRITICAL: Review and fix security warnings"
    fi
    if [[ $warnings -gt 0 ]]; then
        echo "- HIGH: Address system security warnings"
        echo "- HIGH: Implement security patches and updates"
    fi
    echo "- MEDIUM: Regular security updates and patches"
    echo "- MEDIUM: Implement intrusion detection systems"
    echo "- LOW: Regular security audits and assessments"
    echo "- LOW: Implement security monitoring and alerting"
}

generate_network_recommendations() {
    echo "Network Security Recommendations:"
    echo
    echo "- Implement firewall rules to restrict access"
    echo "- Use VPN for remote access"
    echo "- Implement network segmentation"
    echo "- Monitor network traffic for anomalies"
    echo "- Use encrypted communication protocols"
    echo "- Implement proper DNS security"
    echo "- Regular network security assessments"
}

# Function to generate comprehensive security report
generate_comprehensive_report() {
    log_info "Generating comprehensive security report..."
    
    local comprehensive_report="$REPORTS_DIR/comprehensive_security_report_$(date +%Y%m%d_%H%M%S).md"
    
    cat > "$comprehensive_report" << EOF
# MarkItDown Security Audit Report

**Generated:** $(date)  
**Project:** MarkItDown with Vision OCR  
**Audit Type:** Comprehensive Security Assessment

## Executive Summary

This report provides a comprehensive security assessment of the MarkItDown application with Vision OCR integration.

## Container Security

$(cat "$REPORTS_DIR/container_security_summary.txt" 2>/dev/null || echo "Container security scan not completed")

## Code Security

$(cat "$REPORTS_DIR/code_security_summary.txt" 2>/dev/null || echo "Code security analysis not completed")

## Docker Security

$(cat "$REPORTS_DIR/docker_security_summary.txt" 2>/dev/null || echo "Docker security audit not completed")

## System Security

$(cat "$REPORTS_DIR/system_security_summary.txt" 2>/dev/null || echo "System security audit not completed")

## Network Security

$(cat "$REPORTS_DIR/network_security_report.txt" 2>/dev/null || echo "Network security assessment not completed")

## Secrets Management

$(cat "$REPORTS_DIR/secrets_scan_report.txt" 2>/dev/null || echo "Secrets scan not completed")

## Risk Assessment

### High Risk Issues
- Critical vulnerabilities in containers
- Exposed secrets and credentials
- System security warnings

### Medium Risk Issues
- High severity vulnerabilities
- Code security issues
- Docker security misconfigurations

### Low Risk Issues
- Dependency vulnerabilities
- Network security improvements
- Security best practices

## Recommendations

### Immediate Actions
1. Fix critical container vulnerabilities
2. Remove or secure exposed secrets
3. Address system security warnings

### Short-term Actions
1. Update vulnerable dependencies
2. Implement security best practices
3. Configure proper network security

### Long-term Actions
1. Implement security monitoring
2. Regular security audits
3. Security training for development team

## Compliance

This audit helps ensure compliance with:
- OWASP Top 10
- Docker Security Best Practices
- Container Security Standards
- System Security Guidelines

## Next Steps

1. Review all findings and prioritize fixes
2. Implement security recommendations
3. Schedule follow-up security audits
4. Establish security monitoring and alerting

---

*This report was generated automatically by the MarkItDown Security Audit Script*
EOF
    
    log_success "Comprehensive security report generated: $comprehensive_report"
}

# Function to display audit summary
display_audit_summary() {
    log_info "Security audit completed successfully!"
    echo
    echo "=== Security Audit Summary ==="
    echo "Reports generated:"
    echo "- Container security: $REPORTS_DIR/container_security_summary.txt"
    echo "- Code security: $REPORTS_DIR/code_security_summary.txt"
    echo "- Docker security: $REPORTS_DIR/docker_security_summary.txt"
    echo "- System security: $REPORTS_DIR/system_security_summary.txt"
    echo "- Network security: $REPORTS_DIR/network_security_report.txt"
    echo "- Secrets scan: $REPORTS_DIR/secrets_scan_report.txt"
    echo "- Comprehensive report: $REPORTS_DIR/comprehensive_security_report_*.md"
    echo
    echo "=== Next Steps ==="
    echo "1. Review all security reports"
    echo "2. Prioritize and fix security issues"
    echo "3. Implement security recommendations"
    echo "4. Schedule regular security audits"
    echo
    echo "=== Security Tools Used ==="
    echo "- Trivy: Container vulnerability scanning"
    echo "- Bandit: Python code security analysis"
    echo "- Safety: Python dependency vulnerability checking"
    echo "- Docker Bench Security: Docker security audit"
    echo "- Lynis: System security audit"
}

# Main execution
main() {
    echo "=== MarkItDown Security Audit ==="
    echo "This script will perform a comprehensive security audit"
    echo
    
    # Check dependencies
    check_security_dependencies
    
    # Perform security audits
    scan_containers
    analyze_code_security
    audit_docker_security
    audit_system_security
    check_network_security
    check_secrets
    
    # Generate comprehensive report
    generate_comprehensive_report
    
    # Display summary
    display_audit_summary
}

# Run main function
main "$@"
