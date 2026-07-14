from typing import Any, Dict, List
import yaml

class PipelineParserError(Exception):
    pass

class PipelineParser:
    @staticmethod
    def parse_yaml(content: str) -> Dict[str, Any]:
        """
        Parses and validates a YAML CI/CD pipeline schema definition.
        """
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            raise PipelineParserError(f"Invalid YAML syntax: {str(e)}")

        if not isinstance(data, dict):
            raise PipelineParserError("Pipeline configuration must be a dictionary object.")

        stages = data.get("stages")
        if not stages or not isinstance(stages, list):
            raise PipelineParserError("Pipeline must declare a non-empty list of 'stages'.")

        for index, stage in enumerate(stages):
            if not isinstance(stage, dict):
                raise PipelineParserError(f"Stage index {index} is not a valid object.")
            if "name" not in stage:
                raise PipelineParserError(f"Stage index {index} is missing required 'name' field.")

            jobs = stage.get("jobs", [])
            if not isinstance(jobs, list):
                raise PipelineParserError(f"Stage '{stage['name']}' must define a list of 'jobs'.")

            for j_index, job in enumerate(jobs):
                if not isinstance(job, dict):
                    raise PipelineParserError(f"Job index {j_index} in stage '{stage['name']}' is invalid.")
                if "name" not in job:
                    raise PipelineParserError(f"Job index {j_index} in stage '{stage['name']}' is missing 'name'.")

                steps = job.get("steps", [])
                if not isinstance(steps, list) or not steps:
                    raise PipelineParserError(f"Job '{job['name']}' in stage '{stage['name']}' must contain steps list.")

                for s_index, step in enumerate(steps):
                    if not isinstance(step, dict):
                        raise PipelineParserError(f"Step index {s_index} in job '{job['name']}' is invalid.")
                    if "run" not in step:
                        raise PipelineParserError(f"Step index {s_index} in job '{job['name']}' is missing 'run' command.")

        return data
