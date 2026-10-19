# Support incident — recover existing CyberDailyLog Sites publication

Prepared for official OpenAI support on 19 October 2026. This is a prepared
incident, not a submitted ticket. No credentials or signed asset URLs included.

## Subject

CyberDailyLog: production publication remains publishing since 16 October;
recover the same project/deployment without replacing the working public Site.

## Project and symptom

- Site: https://cyberdailylog.jimblogic.chatgpt.site/
- Title: CyberDailyLog Intelligence Dashboard.
- Project: appgprj_6a63172b53c88191b00398c6ccafb36c.
- Current role owner; project active, audience public; do not change audience.
- Provider route: jimblogic--cyberdailylog-dashboard.
- Stuck deployment: appgdep_6ad267b2245481918c1698728d87c52f.
- Version 23: appgprj_6a63172b53c88191b00398c6ccafb36c~appgver_339db2656a20819190e995cc3387d565.
- Exact status: publishing, failure_message=null, url=null, env_set_revision=0.
- Last status update: 2026-10-16T18:07:14.375102Z (20:07:14 Madrid).
- Rechecked on 19 October; the same non-terminal state persists. The platform
  response exposes no reason or supported cancel/restart/recovery operation.

## Recoverable functional version

- Version 22: appgprj_6a63172b53c88191b00398c6ccafb36c~appgver_f211edf3f55481919af6a6e7d90d6bdf.
- Deployment: appgdep_6ad26627df04819181edede4e59d148c.
- Rechecked status: succeeded; public URL is the same Site URL above.
- Success updated_at: 2026-10-16T18:01:11.639891Z.
- Source commit: a2d21bc0b99201959b44791315c0554125996d0c.
- Stored archive SHA-256: c89ef5e3571e784172f7bd0d190852c29f56baaf809dc464e2fe8b0cc7f52ea9.

## Latest saved draft

- Version 26: appgprj_6a63172b53c88191b00398c6ccafb36c~appgver_e2e634e02f3c819185c59ade1f0744ca.
- Source: 4067d080898119dc02ce961dcd87739b540c549e; no deployment attached.
- Archive SHA-256: 7e118c88d4c08bfc645435e39fb06a4350e9f3c328f054618cd5714c755c1672;
  5,908,480 bytes, 84 files.
- Prior verification in this workspace: build, Worker artifact, lint/types and
  32 native tests passed. No visual publication was completed or claimed.

## Reproduction and observed boundaries

1. Query get_deployment_status using the exact project and stuck deployment IDs.
2. It returns publishing and the unchanged 16 October timestamp with no failure.
3. Query the v22 deployment: succeeded. Query saved v26: retained archive/source,
   deployment_id=null. The latest saved version is not a successful publication.
4. Existing Site service HTTPS access serves the new public GitHub CTI report;
   data publication and native UI publication are separate. Last full verified
   service check before this operational task: 19 October 11:15:28 UTC, 11/11.
5. Automated anonymous request from this execution environment receives HTTP
   403. This is not bypassed and is not diagnosed as an application outage.
   Browser QA is unrun; HTTPS checks do not replace it.

No duplicate deployment, new Site, DNS change, unsafe endpoint, credential
exposure or private Guard operation was attempted. Cause remains unknown:
the observable status does not distinguish provider, integration, permissions
or persistent deployment-state defects.

## Requested resolution

Inspect the provider/integration trace for the stuck deployment, recover or
terminate its stale state through supported platform operations, and restore
publishing on **this same Site**. Preserve v22 and all other recoverable versions,
current audience, source archives and public data access. Then allow the intended
saved draft to be published through the normal Sites flow and verify the served
version. Please provide the diagnosed cause and supported recovery operation.

Do not create a replacement Site or change DNS/audience. Do not ask for bearer
tokens, credentials, cookie values or unsanitized network captures in the ticket.

Official submission: https://help.openai.com/ → support chat bubble. Include this
text and the IDs/timestamps. Owner sign-in/account selection and ticket submission
must be performed through the official interface; no account secrets in chat.
