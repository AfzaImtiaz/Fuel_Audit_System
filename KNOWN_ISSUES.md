# Known Issues

## Traccar server errors (open, blocking)

**Status:** Unresolved after two troubleshooting attempts.

**Impact:** Blocks end-to-end testing of WF1 (Daily Reconcile), which blocks:
- generating the real 20-truck demo dataset
- computing a real PKR variance figure
- recording the demo video
- finalizing the pitch deck

**What to try next:**
- [ ] Confirm the exact error message/status code Traccar is returning (attach logs here)
- [ ] Check Traccar server logs directly (`docker logs <container>` if running via Docker)
- [ ] Verify the Traccar API base URL and port in the WF1 "GET Trips" node match the actual running instance
- [ ] Confirm the Traccar API bearer token hasn't expired and belongs to a user with report-read permission
- [ ] Try a clean re-deploy: `docker rm -f traccar && docker run -d --name traccar -p 8082:8082 -p 5055:5055 traccar/traccar:latest`
- [ ] Check that the 20 devices were actually created in Traccar (Settings > Devices) with identifiers matching `Traccar_Device_Id` in `Master_Trucks`
- [ ] If still stuck, ask for help with the exact error message rather than re-attempting the same steps a third time

**Log here what was actually tried**, so the next attempt doesn't repeat the same dead ends:
1. Attempt 1 — [add what was tried and what error resulted]
2. Attempt 2 — [add what was tried and what error resulted]
