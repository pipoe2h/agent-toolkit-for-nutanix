from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
ENTRY = ROOT / "ENTRY.md"
SKILLS_README = ROOT / "skills" / "README.md"
ROADMAP = ROOT / "docs" / "roadmap" / "next-operational-skills.md"

SKILL_PATH = re.compile(r"`(skills/[^`]+)`")
OPERATION_TOKEN = re.compile(
    r"\b(?:get|list|create|update|delete|read|patch|put|post)[A-Z][A-Za-z0-9]*\b"
)
NON_CLAIM_MARKERS = (
    "not verified",
    "unverified",
    "not confirmed",
    "not asserted",
    "no operation",
    "illustrative",
    "example only",
)


def route_rows(path):
    """Return the data rows of every markdown table in a routing document."""
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if not cells or not cells[0]:
            continue
        if set(cells[0]) <= set("-: "):
            continue
        if cells[0].lower() == "user task":
            continue
        rows.append(cells)
    return rows


class EntryRoutingTests(unittest.TestCase):
    def test_skill_paths_referenced_by_router_and_install_notes_exist(self):
        for doc in (ENTRY, SKILLS_README):
            with self.subTest(doc=doc.name):
                referenced = SKILL_PATH.findall(doc.read_text(encoding="utf-8"))
                self.assertTrue(referenced, f"{doc.name} must reference skill paths")
                for relative in referenced:
                    self.assertTrue(
                        (ROOT / relative).is_file(),
                        f"{doc.name} references a path that does not exist: {relative}",
                    )

    def test_route_table_has_no_duplicate_route_rows(self):
        rows = route_rows(ENTRY)
        self.assertTrue(rows, "ENTRY.md must define route rows")
        for row in rows:
            self.assertGreaterEqual(len(row), 2, f"route row is missing columns: {row}")
            self.assertTrue(row[1], f"route row has an empty target: {row}")
        tasks = [row[0].lower() for row in rows]
        duplicates = sorted({task for task in tasks if tasks.count(task) > 1})
        self.assertEqual(duplicates, [], f"duplicate route rows in ENTRY.md: {duplicates}")

    def test_router_is_connect_first_then_operate(self):
        rows = route_rows(ENTRY)
        tasks = [row[0].lower() for row in rows]
        self.assertIn("connect", tasks[0], "the first route must be the connect route")
        operate = [index for index, task in enumerate(tasks) if "operate on it" in task]
        self.assertEqual(
            len(operate), 1, "ENTRY.md needs exactly one 'operate on a connected environment' route"
        )
        operate_index = operate[0]
        self.assertIn(
            "ENTRY.md",
            rows[operate_index][1],
            "the 'already connected / operate' route must point at this route index as the operating entry point",
        )
        inventory = [index for index, task in enumerate(tasks) if "list or report resources" in task]
        self.assertEqual(len(inventory), 1, "ENTRY.md needs exactly one inventory route")
        self.assertLess(
            operate_index, inventory[0], "the operate route must come before the task routes"
        )

    def test_roadmap_does_not_claim_verified_operation_names(self):
        text = ROADMAP.read_text(encoding="utf-8")
        self.assertIn(
            "not verified",
            text.lower(),
            "the roadmap must state that operations, schemas, and permissions are not verified",
        )
        for number, line in enumerate(text.splitlines(), start=1):
            if OPERATION_TOKEN.search(line) and not any(
                marker in line.lower() for marker in NON_CLAIM_MARKERS
            ):
                self.fail(
                    f"{ROADMAP.name}:{number} names an operation without a non-claim marker: {line.strip()}"
                )

    def test_roadmap_states_current_scope_and_candidate_domains(self):
        lowered = ROADMAP.read_text(encoding="utf-8").lower()
        self.assertIn(
            "nutanix-readonly-inventory",
            lowered,
            "the roadmap must name the only implemented operational skill",
        )
        self.assertIn("only", lowered, "the roadmap must state what is implemented today")
        for domain in ("vm lifecycle", "cluster", "network", "alert"):
            self.assertIn(domain, lowered, f"roadmap must list the {domain} candidate domain")
        self.assertIn("evidence", lowered, "the roadmap must state the evidence required")
        self.assertIn("permission", lowered)

    def test_skills_readme_states_installing_skills_does_not_configure_mcp(self):
        lowered = SKILLS_README.read_text(encoding="utf-8").lower()
        self.assertIn("npx", lowered, "skills/README.md must document the npx installer")
        self.assertIn("connectivity", lowered, "skills/README.md must describe the connectivity layer")
        self.assertIn("workflow", lowered, "skills/README.md must describe the workflow layer")
        sentences = re.split(r"(?<=[.!?])\s+", lowered)
        disclaimers = [
            sentence
            for sentence in sentences
            if "does not" in sentence and "mcp" in sentence and ("configure" in sentence or "connect" in sentence)
        ]
        self.assertTrue(
            disclaimers,
            "skills/README.md must state that installing or reading skills does not configure or connect an MCP server",
        )


if __name__ == "__main__":
    unittest.main()
