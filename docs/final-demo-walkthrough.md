# BizBridge final demo walkthrough (about 8 minutes)

Use this guide to record the required 5–10 minute prototype demonstration. Keep the browser zoom at 90–100%, close unrelated tabs, and record the browser plus your narration.

## Before recording

1. Open the live website linked in the README: https://bizbridge-coz9.onrender.com
2. If the Render free service has been idle, allow up to about one minute for its first page load.
3. Confirm that you can sign in with the demo accounts listed in the README. The current documented demo password is `DemoAccess!2026`.
4. Check that the demo accounts and sample records exist. The seed command creates:
   - `demo_founder` — entrepreneur (Aline / Demo GreenGrow Rwanda)
   - `demo_partner` — entrepreneur (Jean / Demo AgroLink Logistics)
   - `demo_mentor` — verified mentor (Maya)
   - `demo_investor` — verified investor (Eric)
   - `demo_admin` — staff account for the admin console
5. If a demo login fails, do not spend the recording troubleshooting it. Check the Render service's `DEMO_PASSWORD` environment variable and confirm the seed command ran. Existing demo-account passwords are not automatically reset by a normal re-seed.
6. Do not present sample opportunities as real open funding calls. The seeded examples are clearly labelled `[DEMO]`.

## Suggested recording

| Time | What to show | What to explain |
|---|---|---|
| 0:00–0:40 | Landing page | Introduce the problem: entrepreneurs often have to search across separate channels to find mentors, investors, partners and opportunities. BizBridge brings discovery and connection into one platform. |
| 0:40–1:10 | Help page and navigation | Briefly show the user roles and the main areas of the platform. |
| 1:10–2:00 | Sign in as `demo_founder`; show the dashboard | Explain the entrepreneur profile, role-aware dashboard, notifications and recommended matches. |
| 2:00–2:45 | Edit profile and recommendations | Show business name, sector, stage and location. Explain that version-one recommendations use transparent rules based on sector, stage and location—not AI matching. |
| 2:45–3:35 | People directory at `/people/` | Search for a mentor, investor or business. Apply a sector, location or stage filter and open a profile. |
| 3:35–4:20 | Opportunities at `/opportunities/` | Show the opportunity categories, a sample opportunity detail page and how expired opportunities are excluded. Point out the `[DEMO]` label on sample records. |
| 4:20–5:15 | Mentorship and investor request pages | Show the entrepreneur's request workflow and the request status. If the seeded requests have already been handled, create a fresh test request before switching accounts. |
| 5:15–6:10 | Sign in as `demo_mentor` and/or `demo_investor` | Show the incoming request and the accept/decline action. Explain that the mentor and investor have separate role-specific dashboards and actions. |
| 6:10–6:55 | Messages at `/messages/` | Show the accepted connection and sample conversation between the founder and partner. Explain that messaging is available after a connection is accepted. |
| 6:55–7:40 | Sign in as `demo_admin`; open `/manage/` | Show the staff dashboard, user management, profile verification, opportunity management and activity report/CSV option. Do not change or delete demo records during the recording. |
| 7:40–8:10 | Return to landing page or show the repository | Summarise the value of the platform and mention the main implementation technologies: Python, Django, HTML/CSS, SQLite locally and PostgreSQL on Render. |

You do not need to show every row if the recording is running long. Prioritise the complete entrepreneur journey, one request response, messaging and the admin view.

## Suggested closing

“BizBridge is a role-based entrepreneurship support platform. It helps entrepreneurs complete a profile, discover relevant people and opportunities, request mentorship or investor introductions, and continue accepted connections through messaging. Mentors, investors and administrators each have their own workflows. The current matching approach is rule-based and explainable; AI matching, payments, video calls and a mobile app are outside this first version.”

## Final submission checks

- [ ] The public website URL opens and the demo login works.
- [ ] The GitHub repository is public and the submitted repository link opens.
- [ ] The SRS/system-design link is added to the README (replace the current “add your SRS link here” placeholder).
- [ ] The recorded video is between 5 and 10 minutes and demonstrates the implemented workflows.
- [ ] The submission includes the website URL, repository URL, SRS link and video link.
