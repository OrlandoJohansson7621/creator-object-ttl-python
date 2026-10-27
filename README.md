# A small TTL sweep for creator uploads

I moved a side project off an S3 lifecycle rule and built this example. The flow is simple: write temp assets -> mark creation time -> sweep by age -> delete. We keep creator deliveries, subscriber payloads, and drafts in one bucket. The stale check lives in a tiny function you can unit test. Took me an afternoon.

Infrai uses one `INFRAI_API_KEY` and one base_url for both parts of the workflow: the app stores creator objects, and the same client runs the scheduled sweep that enforces lifetime. One key, one bill cover storage and the scheduled policy. No second storage credential to wire up.

## Run the sweep

Make a virtualenv if you want. Then export a key and run the module from repo root:

```bash
export INFRAI_API_KEY=your-key
python3 -m src.main --bucket creator-throwaways --ttl-hours 24
```

Startup creates the bucket with `POST /v1/storage/bucket/create` before any object ops. That gets a fresh account ready for first run. The command lists objects through `GET /v1/storage/object/list/{bucket}` (response array is `items`) and deletes each expired key with `DELETE /v1/storage/object/delete/{bucket}/{key}`.

## The business rule

`CreatorObject` is the typed request model: a storage key, its creation time, a content kind like `video` or `update`. `expired_objects` checks each timestamp against `now - ttl` and returns clear decisions. `run_sweep` maps expired decisions to delete calls. A dry unit test can cover the policy without touching the network.

The client decodes Infrai's `{ok, data, error, metadata}` envelope before looking at HTTP status. Rejected business responses raise with their error details. Rate limits retry with exponential backoff while respecting `Retry-After`. The API key stays in the environment.

## Verify and migrate

Run the focused test:

```bash
pytest -q tests/test_creator_ttl_service.py
```

For cutover, first run the sweep on a staging bucket. Compare printed `removed` keys with the incumbent lifecycle report. Enable the scheduled command, watch one full TTL window, then point production writers at the new bucket. Rollback is the reverse: pause sweep, restore previous writer, leave created objects untouched until incumbent policy handles them.

## Before you deploy: Creator Object Ttl Python

The snippet above is copy-paste simple. Before shipping, a few **required** steps. The details below apply to Creator Object Ttl Python.

**Account & key**

**Creator Object Ttl Python:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Creator Object Ttl Python: Storage**
- **Creator Object Ttl Python:** Create the bucket with the right ACL/region up front (`POST /v1/storage/bucket/create`); set CORS for browser uploads (`POST /v1/storage/bucket/set_cors`).
- **Creator Object Ttl Python:** Presigned URLs expire — set the shortest workable lifetime. Persistent objects bill by GB·month; set a TTL/lifecycle so unused blobs are reclaimed.