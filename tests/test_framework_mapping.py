from sec_evidence.framework_mapping import references_for_check


def test_required_reviews_maps_to_iso_and_nis2_references() -> None:
    references = references_for_check("github.branch.required_reviews")
    keys = {(item["framework"], item["reference"]) for item in references}
    assert ("ISO_IEC_27001_2022", "A.8.32") in keys
    assert ("NIS2_2022_2555", "Article 21(2)(e)") in keys
    assert all(item["relationship"] == "supports" for item in references)


def test_unmapped_check_has_no_framework_claim() -> None:
    assert references_for_check("github.repository.visibility") == []
