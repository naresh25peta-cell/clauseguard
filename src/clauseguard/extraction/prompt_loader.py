"""
prompt_loader.py — loads the standard intro and per-field specs from the prompt files.

Why files instead of hardcoded strings?
  Storing prompts as markdown files means subject-matter experts can review and edit
  them without touching Python code.

Each field is defined by:
  - name         : matches the RulesDB column name (e.g. "AgreementSection")
  - output_type  : free text description or "One of: a, b, c" for categorical fields
  - instruction  : the actual extraction instruction sent to the LLM
  - allowed_values: parsed from output_type if categorical, else None
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


@dataclass(frozen=True)
class FieldSpec:
    name: str
    output_type: str
    instruction: str
    open_question: str

    @property
    def allowed_values(self) -> list[str] | None:
        """Parse 'One of: a, b, c' into a list. Returns None for free-text fields."""
        prefix = "One of:"
        if not self.output_type.startswith(prefix):
            return None
        rest = self.output_type[len(prefix):].strip()
        # Strip trailing " or blank" qualifier if present
        rest = rest.replace(", or blank", "").replace(" or blank", "")
        return [v.strip() for v in rest.split(",") if v.strip()]


def load_standard_intro() -> str:
    """Read the shared standard intro from 00_standard_intro.md."""
    path = PROMPTS_DIR / "00_standard_intro.md"
    text = path.read_text(encoding="utf-8")
    # Strip the markdown heading — return just the prose
    lines = [l for l in text.splitlines() if not l.startswith("#")]
    return "\n".join(lines).strip()


def load_fields() -> list[FieldSpec]:
    """Parse each numbered prompt file (01_*.md … 07_*.md) into a FieldSpec."""
    fields = []
    for md_file in sorted(PROMPTS_DIR.glob("[0-9][1-9]_*.md")):
        text = md_file.read_text(encoding="utf-8")
        fields.append(_parse_field_md(text))
    return fields


def _parse_field_md(text: str) -> FieldSpec:
    """Extract name, output_type, instruction, and open_question from a prompt file."""
    lines = text.splitlines()

    # Field name = first H1 heading
    name = next((l.lstrip("# ").strip() for l in lines if l.startswith("# ")), "")

    # output_type = value after "**Output type / allowed values:**"
    output_type = ""
    for line in lines:
        if "Output type / allowed values" in line:
            output_type = line.split(":**")[-1].strip()
            break

    # open_question = value after "**Open question for SME:**"
    open_question = ""
    for line in lines:
        if "Open question for SME" in line:
            open_question = line.split(":**")[-1].strip().strip("_")
            break

    # instruction = everything after "## Extraction instruction" up to end of file,
    # excluding the blockquote line that references the standard intro
    instruction_lines = []
    in_instruction = False
    for line in lines:
        if line.startswith("## Extraction instruction"):
            in_instruction = True
            continue
        if in_instruction:
            if line.startswith("> Standard intro"):
                continue  # skip the "see 00_standard_intro.md" reminder line
            instruction_lines.append(line)

    instruction = "\n".join(instruction_lines).strip()

    return FieldSpec(
        name=name,
        output_type=output_type,
        instruction=instruction,
        open_question=open_question,
    )
