from __future__ import annotations

from .session import create_client


class EcrReadonlyClient:
    def __init__(self, region: str, profile: str | None) -> None:
        self.region = region
        self.profile = profile

    def image_exists(
        self,
        repository_name: str,
        image_tag: str | None = None,
        image_digest: str | None = None,
    ) -> tuple[bool, str, dict]:
        client_result = create_client("ecr", self.region, self.profile)
        if not client_result.ok:
            return False, client_result.error or "Unable to create ECR client.", {}

        image_id: dict[str, str] = {}
        if image_digest:
            image_id["imageDigest"] = image_digest
        else:
            image_id["imageTag"] = image_tag or "latest"

        try:
            response = client_result.client.describe_images(
                repositoryName=repository_name,
                imageIds=[image_id],
            )
        except Exception as exc:
            return False, f"ECR image lookup failed for {repository_name}:{image_tag or image_digest}: {exc}", {}

        details = response.get("imageDetails", [])
        if not details:
            return False, f"ECR repository {repository_name} was found, but the requested image was not present.", {}

        detail = details[0]
        pushed_at = str(detail.get("imagePushedAt", "unknown"))
        digest = detail.get("imageDigest", "unknown")
        tags = detail.get("imageTags", [])
        return (
            True,
            f"ECR image exists in repository {repository_name}. Digest: {digest}. Pushed at: {pushed_at}.",
            {"image_digest": digest, "image_tags": tags, "image_pushed_at": pushed_at},
        )
