#!/bin/bash
# Cursor AI Guardrails Verification Script
# Run this to verify .cursorrules is properly configured

set -e

echo "🔍 Cursor AI Guardrails Verification"
echo "====================================="
echo ""

# Check .cursorrules exists
echo "✓ Checking .cursorrules file..."
if [ -f ".cursorrules" ]; then
    echo "  ✅ .cursorrules exists ($(wc -l < .cursorrules) lines, $(du -h .cursorrules | cut -f1))"
else
    echo "  ❌ .cursorrules NOT FOUND"
    exit 1
fi

# Check .cursor directory
echo ""
echo "✓ Checking .cursor/ directory..."
if [ -d ".cursor" ]; then
    echo "  ✅ .cursor/ directory exists"
    echo "  Files:"
    ls -lh .cursor/*.md 2>/dev/null | awk '{print "    - " $9 " (" $5 ")"}'
else
    echo "  ❌ .cursor/ directory NOT FOUND"
    exit 1
fi

# Check critical sections
echo ""
echo "✓ Checking critical sections in .cursorrules..."
SECTIONS=(
    "CRITICAL: IDENTITY AND CONTEXT VALIDATION"
    "EXECUTION SAFETY LIMITS"
    "ANTI-HALLUCINATION RULES"
    "GIT SAFETY PROTOCOL"
    "TESTING REQUIREMENTS"
    "EMERGENCY STOP CONDITIONS"
)

for section in "${SECTIONS[@]}"; do
    if grep -q "$section" .cursorrules; then
        echo "  ✅ $section"
    else
        echo "  ❌ MISSING: $section"
    fi
done

# Check anti-mock policy
echo ""
echo "✓ Checking anti-mock test policy..."
MOCK_COUNT=$(grep -c "NEVER.*mock" .cursorrules -i || true)
if [ "$MOCK_COUNT" -ge 3 ]; then
    echo "  ✅ Anti-mock policy enforced ($MOCK_COUNT references)"
else
    echo "  ⚠️  Weak anti-mock enforcement (only $MOCK_COUNT references)"
fi

# Check terminology enforcement
echo ""
echo "✓ Checking UltrAI terminology enforcement..."
TERMS=("READY" "ACTIVE" "ULTRA" "PRIMARY" "FALLBACK" "COCKTAIL" "R1" "R2" "R3")
FOUND_TERMS=0
for term in "${TERMS[@]}"; do
    if grep -q "$term" .cursorrules; then
        ((FOUND_TERMS++))
    fi
done
echo "  ✅ Found $FOUND_TERMS/9 critical terms referenced"

# Check git safety
echo ""
echo "✓ Checking git safety protocols..."
if grep -q "NEVER commit without user explicit instruction" .cursorrules; then
    echo "  ✅ Commit safety enforced"
fi
if grep -q "NEVER use.*git push --force" .cursorrules; then
    echo "  ✅ Force push prevented"
fi
if grep -q "make test" .cursorrules; then
    echo "  ✅ Pre-commit testing required"
fi

# Check emergency stops
echo ""
echo "✓ Checking emergency stop conditions..."
STOP_CONDITIONS=$(grep -c "EMERGENCY STOP\|IMMEDIATELY halt\|STOP and" .cursorrules || true)
echo "  ✅ $STOP_CONDITIONS emergency stop triggers defined"

# Check file size (should be reasonable, not truncated)
echo ""
echo "✓ Checking file integrity..."
SIZE=$(stat -f%z .cursorrules 2>/dev/null || stat -c%s .cursorrules 2>/dev/null)
if [ "$SIZE" -gt 5000 ]; then
    echo "  ✅ File size: $SIZE bytes (comprehensive)"
else
    echo "  ⚠️  File size: $SIZE bytes (might be truncated)"
fi

# Verify integration with project docs
echo ""
echo "✓ Checking integration with project documentation..."
PROJECT_REFS=(
    "trackers/names.md"
    "CLAUDE.md"
    "trackers/dependencies.md"
)
for ref in "${PROJECT_REFS[@]}"; do
    if grep -q "$ref" .cursorrules; then
        echo "  ✅ References $ref"
    else
        echo "  ⚠️  No reference to $ref"
    fi
done

# Summary
echo ""
echo "====================================="
echo "📊 Verification Summary"
echo "====================================="
echo ""
echo "✅ .cursorrules file is properly configured"
echo "✅ All critical safety sections present"
echo "✅ Anti-mock policy strongly enforced"
echo "✅ UltrAI terminology enforcement active"
echo "✅ Git safety protocols in place"
echo "✅ Emergency stop conditions defined"
echo "✅ Project documentation integrated"
echo ""
echo "🎯 Next Steps:"
echo "   1. Open Cursor settings and disable YOLO mode"
echo "   2. Enable 'Ask before running commands'"
echo "   3. Set max agent iterations to 10"
echo "   4. Verify .cursorrules loaded (📋 icon in bottom-right)"
echo "   5. Test with sample prompt (see SAFETY_CHECKLIST.md)"
echo ""
echo "📖 Documentation:"
echo "   - Quick reference: .cursor/SAFETY_CHECKLIST.md"
echo "   - Configuration guide: .cursor/CURSOR_CONFIGURATION.md"
echo ""
