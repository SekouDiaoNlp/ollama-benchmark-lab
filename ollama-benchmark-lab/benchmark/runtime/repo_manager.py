from pathlib import Path


class RepoManager:

    def get_repo(self, repo_url: str, commit: str) -> Path:

        repo_path = self._checkout(repo_url, commit)

        print(f"[REPO MANAGER DEBUG] raw repo_path type={type(repo_path)} value={repo_path}")

        repo_path = Path(repo_path)

        print(f"[REPO MANAGER DEBUG] normalized repo_path type={type(repo_path)} value={repo_path}")

        if not repo_path.exists():
            print(f"[REPO MANAGER DEBUG] PATH DOES NOT EXIST: {repo_path}")
            raise FileNotFoundError(repo_path)

        print(f"[REPO MANAGER DEBUG] OK EXISTS: {repo_path}")
        return repo_path

    def _checkout(self, repo_url: str, commit: str):

        path = f".cache/repos/{commit}"

        print(f"[REPO MANAGER DEBUG] checkout repo_url={repo_url} commit={commit} -> {path}")

        return path