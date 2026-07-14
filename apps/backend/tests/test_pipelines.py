from uuid import uuid4
import pytest
from src.core.pipeline_parser import PipelineParser, PipelineParserError
from src.models.pipeline import Pipeline, PipelineRun

# ==========================================
# Unit Tests: Pipeline Parser
# ==========================================

def test_pipeline_parser_valid_yaml() -> None:
    yaml_data = """
stages:
  - name: build
    jobs:
      - name: compile
        steps:
          - name: run-build
            run: npm run build
"""
    parsed = PipelineParser.parse_yaml(yaml_data)
    assert parsed["stages"][0]["name"] == "build"
    assert parsed["stages"][0]["jobs"][0]["name"] == "compile"

def test_pipeline_parser_invalid_yaml() -> None:
    bad_yaml = """
stages:
  - name: build
  jobs:
    - broken indent
"""
    with pytest.raises(PipelineParserError):
        PipelineParser.parse_yaml(bad_yaml)

# ==========================================
# Unit Tests: Models
# ==========================================

def test_pipeline_model_creation() -> None:
    project_id = uuid4()
    pipeline = Pipeline(
        project_id=project_id,
        name="Production Build Pipeline",
        slug="production-build-pipeline",
        description="Automated continuous builds"
    )
    assert pipeline.name == "Production Build Pipeline"
    assert pipeline.slug == "production-build-pipeline"
    assert pipeline.project_id == project_id
