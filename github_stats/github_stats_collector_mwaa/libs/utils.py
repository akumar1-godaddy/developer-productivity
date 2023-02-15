
from github import GithubObject, PaginatedList, WorkflowRun, Branch
from github.NamedUser import NamedUser


def get_workflow_runs(
        repo=str,
        org_name=str,
        actor=GithubObject.NotSet,
        branch=GithubObject.NotSet,
        event=GithubObject.NotSet,
        status=GithubObject.NotSet,
        created=GithubObject.NotSet,
        requester=GithubObject.NotSet
):
    """
    :param repo:
    :param org_name:
    :param created:
    :calls: `GET /repos/{owner}/{repo}/actions/runs <https://docs.com/en/rest/reference/actions#list-workflow-runs-for-a-repository>`_
    :param actor: :class:`NamedUser.NamedUser` or string
    :param branch: :class:`Branch.Branch` or string
    :param event: string
    :param status: string `queued`, `in_progress`, `completed`, `success`, `failure`, `neutral`, `cancelled`, `skipped`, `timed_out`, or `action_required`

    :rtype: :class:`PaginatedList.PaginatedList` of :class:`WorkflowRun.WorkflowRun`
    """
    assert (
            actor is GithubObject.NotSet
            or isinstance(actor, NamedUser.NamedUser)
            or isinstance(actor, str)
    ), actor
    assert (
            branch is GithubObject.NotSet
            or isinstance(branch, Branch.Branch)
            or isinstance(branch, str)
    ), branch
    assert event is GithubObject.NotSet or isinstance(event, str), event
    assert status is GithubObject.NotSet or isinstance(status, str), status
    assert created is GithubObject.NotSet or isinstance(created, str), created

    url_parameters = dict()
    if actor is not GithubObject.NotSet:
        if isinstance(actor, NamedUser.NamedUser):
            url_parameters["actor"] = actor._identity
        else:
            url_parameters["actor"] = actor
    if branch is not GithubObject.NotSet:
        if isinstance(branch, Branch.Branch):
            url_parameters["branch"] = branch.name
        else:
            url_parameters["branch"] = branch
    if event is not GithubObject.NotSet:
        url_parameters["event"] = event
    if status is not GithubObject.NotSet:
        url_parameters["status"] = status
    if created is not GithubObject.NotSet:
        url_parameters["created"] = created

    return PaginatedList.PaginatedList(
        WorkflowRun.WorkflowRun,
        requester,
        f"https://api.github.com/repos/{org_name}/{repo}/actions/runs",
        url_parameters,
        list_item="workflow_runs",
    )
