# Jevin

Jevin is an agentic property-search and relocation assistant built for
the **All Things Agentic Hackathon** using Gemini 3.5 Flash, Google
Agent Development Kit (ADK), Vertex AI and Google Cloud Run.

Rather than giving one AI agent every tool and the entire conversation
context, Jevin explores a model of **considered delegation**: specialist
agents have bounded responsibilities and exchange only the information
needed to complete their part of a workflow.

## The problem

Finding a rental property is not a single search task. A potential home
may meet the rental budget but still be unsuitable because of transport,
access to shops and services, or the practicalities of living in the
surrounding area. Jevin turns this into a coordinated workflow.

## Architecture

### Jevin --- Property Search Coordinator

Jevin is the root ADK agent. Jevin can:

-   establish the client's location and rental budget
-   perform rental-market budget checks
-   search property data through the Property Market Intel API
-   identify candidates that require further investigation
-   decide when specialist local-area research is useful
-   delegate that research to Jimothy
-   retrieve the resulting research
-   synthesise property and local-area information for the client

### Jimothy --- Local Area Specialist

Jimothy is a bounded ADK sub-agent responsible for investigating what
life around a potential property would actually be like. Research can
include public transport, shops and services, access to nearby towns,
local amenities and other practical limitations relevant to the move.

Jimothy uses Google Search for local-area research.

### The Green Room --- Shared Coordination State

The Green Room is not another agent. It is a lightweight coordination
layer implemented using ADK shared session state.

When Jevin needs specialist research, he places a concise work packet
into the Green Room containing the property location, a concise property
summary and a specific research request. Jimothy retrieves that
information, performs the research and returns his report to the Green
Room. Jevin then retrieves the completed report and incorporates it into
his response.

**Client → Jevin → Green Room → Jimothy → Green Room → Jevin → Client**

This allows agents to collaborate without automatically sharing the
entire conversation.

## Considered Delegation

A core design principle of Jevin is **considered delegation**. Adding
more agents does not automatically make an agentic system better.

Before delegating, the system should effectively ask:

-   Is specialist work actually required?
-   Which specialist should perform it?
-   What information does that specialist need?
-   What tools and authority should they have?
-   When should control return to the human?

During testing, Jevin correctly avoided delegating to Jimothy when no
suitable property candidate existed to investigate. Autonomy therefore
includes knowing when **not** to delegate.

## Technology

-   Python
-   Gemini 3.5 Flash
-   Google Agent Development Kit (ADK)
-   Vertex AI
-   Google Cloud Run
-   Google Secret Manager
-   Google Search
-   Property Market Intel API

## Google Cloud Deployment

The application is deployed from source to Google Cloud Run.

Sensitive credentials are excluded from the deployment source. The
Property Market Intel API key is stored in Google Secret Manager and
injected into the Cloud Run service at runtime rather than being
committed to source control.

The deployed ADK service exposes `jevin_agent` as an available
application.

## Running Jevin Locally

### Prerequisites

You will need:

-   Python 3
-   a Google Cloud project
-   access to Gemini 3.5 Flash through Vertex AI
-   Google Cloud authentication configured locally
-   a Property Market Intel API key

### 1. Clone the repository

``` bash
git clone <REPOSITORY_URL>
cd jevin
```

Replace `<REPOSITORY_URL>` with the repository URL.

### 2. Create a virtual environment

``` bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

``` bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create `jevin_agent/.env` containing:

``` text
GOOGLE_GENAI_USE_ENTERPRISE=1
GOOGLE_CLOUD_PROJECT=YOUR_GOOGLE_CLOUD_PROJECT_ID
GOOGLE_CLOUD_LOCATION=global
PMI_API_KEY=YOUR_PROPERTY_MARKET_INTEL_API_KEY
```

Do not commit this file to source control.

### 5. Authenticate with Google Cloud

``` bash
gcloud auth application-default login
gcloud config set project YOUR_GOOGLE_CLOUD_PROJECT_ID
```

### 6. Run the ADK application

From the repository root:

``` bash
adk web
```

Open the local ADK interface shown in the terminal and select
`jevin_agent`.

## Deploying to Google Cloud Run

Required Google Cloud services include Vertex AI, Cloud Run, Cloud
Build, Artifact Registry and Secret Manager.

The `PMI_API_KEY` secret should be created in Google Secret Manager and
made available to the Cloud Run runtime identity.

Deploy from the repository root:

``` bash
gcloud run deploy jevin-agent \
  --source . \
  --region=YOUR_REGION \
  --allow-unauthenticated \
  --set-env-vars="GOOGLE_GENAI_USE_ENTERPRISE=1,GOOGLE_CLOUD_PROJECT=YOUR_GOOGLE_CLOUD_PROJECT_ID,GOOGLE_CLOUD_LOCATION=global" \
  --set-secrets="PMI_API_KEY=PMI_API_KEY:latest"
```

After deployment, check:

``` text
https://YOUR_CLOUD_RUN_SERVICE_URL/list-apps
```

A successful deployment should include:

``` json
["jevin_agent"]
```

## Data limitations

Property availability is obtained through the Property Market Intel API.
A property returned by an external API should not automatically be
interpreted as guaranteed current availability on every consumer
property portal.

This project treats **agent orchestration** and **external data
freshness** as separate engineering concerns. Future versions will
explore stronger freshness verification and clearer confidence
information.

## What's Next

The architecture is designed to expand through additional bounded
specialists rather than continually adding tools to one large agent.

### Ellie --- Communication and Viewing Specialist

Ellie is the next planned specialist and is represented in the project
architecture.

Once Jevin identifies a promising property and Jimothy completes the
local-area investigation, the future workflow is designed to:

1.  combine the findings into a recommendation
2.  generate a printable PDF property report
3.  return the decision to the client
4.  ask whether the client wants to pursue a viewing
5.  delegate to Ellie only after client approval

Ellie's planned responsibilities include property enquiry emails,
viewing correspondence, calendar availability, appointment coordination
and helping arrange property viewings.

Actions such as sending communications or confirming appointments can
remain subject to explicit human approval.

**Client → Find → Investigate → Recommend → Report → Ask Client → Act**

The aim is not maximum automation. It is useful autonomy while keeping
the human above the system.

## Project Status

### Implemented

-   Jevin root agent
-   property-search tools
-   Jimothy specialist sub-agent
-   Google Search integration
-   Green Room shared-state coordination
-   conditional agent delegation
-   end-to-end Jevin → Jimothy → Jevin workflow
-   Gemini 3.5 Flash / Vertex AI integration
-   Google Cloud Run deployment
-   Secret Manager integration

### Planned

-   Ellie communication and appointment specialist
-   printable PDF property reports
-   viewing approval workflow
-   email integration
-   calendar integration
-   enhanced property freshness verification
-   richer Green Room task state and provenance

## Hackathon

This project was created for entry into the **All Things Agentic
Hackathon**.

The project explores how bounded specialist agents, shared working state
and considered delegation can turn a messy real-world task into a
coordinated agentic workflow.

## Reproducible Testing

1. Complete the local setup above and start the application with `adk web`.
2. Open the ADK web interface and select `jevin_agent`.
3. Ask Jevin to find rental properties in a location with a specified maximum budget.
4. For a viable candidate, verify that Jevin searches the property data, stores the candidate in the Green Room, delegates local-area research to Jimothy, retrieves Jimothy's report, and returns a combined assessment.
5. Repeat with criteria for which no viable property is found and verify that Jevin does not unnecessarily delegate to Jimothy.
6. For the deployed Cloud Run service, visit `/list-apps` and verify that `jevin_agent` is returned.
