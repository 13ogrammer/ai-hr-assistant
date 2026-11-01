from shared.access import ACCESS_LEVELS, access_level_for_doc, allowed_roles_for_level


def test_unlisted_doc_defaults_to_internal():
    assert access_level_for_doc("02_ANNUAL_LEAVE_POLICY.md") == "internal"


def test_listed_docs_get_their_configured_level():
    assert access_level_for_doc("11_CEO_EMPLOYMENT_CONTRACT_RESTRICTED.md") == "restricted"
    assert access_level_for_doc("12_MANAGER_COMPENSATION_CALIBRATION_GUIDE.md") == "confidential"


def test_every_access_level_has_a_non_empty_role_list():
    for level, roles in ACCESS_LEVELS.items():
        assert allowed_roles_for_level(level) == roles
        assert len(roles) > 0


def test_restricted_is_hr_only():
    assert allowed_roles_for_level("restricted") == ["hr"]


def test_internal_is_every_role():
    assert set(allowed_roles_for_level("internal")) == {"employee", "manager", "hr"}
