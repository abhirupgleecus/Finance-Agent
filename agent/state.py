from agent.schemas import FinancialProfile


def merge_profiles(
    existing: FinancialProfile,
    new: FinancialProfile
) -> FinancialProfile:
    """
    Merge new extracted data into existing state.
    Only updates fields that are not None.
    """

    updated_data = existing.dict()

    for field, value in new.dict().items():
        if value is not None:
            updated_data[field] = value

    return FinancialProfile(**updated_data)


def get_missing_fields(profile: FinancialProfile) -> list[str]:
    """
    Returns list of missing fields in the profile.
    """
    missing = []

    for field, value in profile.dict().items():
        if value is None:
            missing.append(field)

    return missing