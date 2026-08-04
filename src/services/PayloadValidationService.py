
from pydantic import ValidationError
from src.models.payload_model import MortgagePayload
class PayloadValidationService:
    """Validate incoming mortgage underwriting payloads using Pydantic."""

    def validate_payload(self, payload: Any) -> tuple[bool, list[str]]:
        if not isinstance(payload, dict):
            return False, ['Payload must be a JSON object.']

        try:
            MortgagePayload.model_validate(payload)
        except ValidationError as exc:
            errors = []
            for issue in exc.errors():
                field_name = '.'.join(str(item) for item in issue['loc'])
                errors.append(f'{field_name}: {issue["msg"]}')
            return False, errors

        return True, []