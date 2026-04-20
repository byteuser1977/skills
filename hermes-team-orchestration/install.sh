#!/bin/bash
# Install Hermes Team Orchestration skill to Hermes Agent
# Usage: ./install.sh

set -e

HERMES_ROOT="${HOME}/.hermes"
SKILL_DIR="${HERMES_ROOT}/skills/hermes-team-orchestration"
TOOLS_DIR="${HERMES_ROOT}/hermes-agent/tools"

echo "Installing hermes-team-orchestration..."

# Create directories
mkdir -p "${SKILL_DIR}"
mkdir -p "${TOOLS_DIR}"

# Copy files
cp -r /tmp/hermes-team-orchestration/* "${SKILL_DIR}/"

# Create symlink in tools for auto-registration (option 1)
# Or copy directly (option 2)
ln -sf "${SKILL_DIR}/tools/hermes_team_orchestration_register.py" \
       "${TOOLS_DIR}/hermes_team_orchestration.py"

# Alternatively, if you prefer copy:
# cp "${SKILL_DIR}/tools/hermes_team_orchestration_register.py" \
#    "${TOOLS_DIR}/hermes_team_orchestration.py"

echo "✅ Installed!"
echo
echo "Next steps:"
echo "1. Create team config in your workspace:"
echo "   .hermes-team/config.yaml (see ${SKILL_DIR}/config.yaml.template)"
echo
echo "2. In Hermes, load the skill:"
echo "   /load skill hermes-team-orchestration"
echo
echo "3. Initialize your team:"
echo "   >>> hto_init_team(config=..., workspace=\"/path/to/project\")"
echo
echo "Or use manually:"
echo "   import hermes_team_orchestration as hto"
echo "   hto.init_team(config, workspace=\"/path/to/project\")"