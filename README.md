# Aster & Row AI Customer Support Agent

An AI-powered customer support agent for **Aster & Row** that answers customer questions using a grounded knowledge base and verified order information.

The project focuses on reliable customer support behavior, including policy grounding, order lookups, source authority, prompt-injection resistance, privacy protection, and safe escalation to human support when the available information is insufficient or conflicting.

---

## Features

* Knowledge-base retrieval for customer support questions
* Grounded responses based only on supplied company documents
* Authority-aware handling of official vs. draft/internal documents
* Verified order lookup using the provided order tool
* Safe handling of missing, malformed, and unknown order IDs
* Deterministic handling of order status and delivery information
* Return-policy support, including:

  * Standard return window
  * TrailPlus return window
  * Final-sale damaged/defective exceptions
* International shipping policy handling
* Prompt-injection detection and protection
* Sensitive/private information protection
* Insufficient-information detection
* Source-conflict detection
* Human-support escalation for cases that cannot be safely resolved
* Source citations in knowledge-base responses

---

## Project Structure

```text
ai-agent-intern-test/
│
├── app/
│   ├── __init__.py
│   ├── agent.py
│   ├── config.py
│   ├── main.py
│   │
│   ├── memory/
│   │   ├── __init__.py
│   │   └── session.py
│   │
│   ├── retrieval/
│   │   ├── __init__.py
│   │   ├── loader.py
│   │   └── retriever.py
│   │
│   ├── safety/
│   │   ├── __init__.py
│   │   └── guardrails.py
│   │
│   └── tools/
│       ├── __init__.py
│       └── orders.py
│
├── scripts/
│   └── smoke_test.py
│
├── tests/
│   ├── test_orders.py
│   └── test_retrieval.py
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## How It Works

The agent follows a simple support pipeline:

```text
User question
     │
     ▼
Safety / privacy checks
     │
     ▼
Intent detection
     │
     ├── Order question ──► Order Lookup Tool
     │
     └── Policy question ─► Knowledge Retrieval
                                  │
                                  ▼
                           Authority filtering
                                  │
                                  ▼
                         Grounded response
                                  │
                                  ▼
                         Safety validation
                                  │
                                  ▼
                         Customer response
```

The application does not treat retrieved documents as instructions. Retrieved content is treated as data and is used only as evidence for answering the customer's question.

---

## Knowledge Grounding

The agent uses the supplied Aster & Row knowledge base to answer policy and product questions.

Retrieved documents contain metadata such as:

* filename
* heading
* document status
* audience
* policy authority
* customer-answering status
* document content

The agent prioritizes active, official, customer-facing policies over draft, migration, scratchpad, vendor, or superseded material.

This prevents outdated or internal documents from silently overriding the current customer-facing policy.

---

## Order Lookup

Order-specific information is obtained through the `OrderLookup` tool.

The agent does not invent:

* order status
* carrier
* tracking number
* delivery date
* order information

Supported order scenarios include:

* valid order IDs
* lowercase/whitespace-normalized order IDs
* unknown orders
* malformed order IDs
* missing order IDs
* cancelled orders
* shipped orders
* shipped orders without an ETA
* delivered orders
* delivery exceptions

Cancelled orders do not expose stale carrier, tracking, or delivery information.

When a shipped order has no delivery estimate, the agent explicitly states that the delivery estimate is unavailable instead of inventing an arrival date.

---

## Safety and Guardrails

The agent includes several safety controls.

### Prompt Injection

User messages are treated as untrusted input.

The agent does not follow instructions contained inside:

* retrieved documents
* migration notes
* internal notes
* tool results
* other untrusted content

For example, an internal migration document cannot override the active official return policy.

The agent explicitly identifies non-authoritative material when handling prompt-injection scenarios and uses the current official policy instead.

### Sensitive Information

The agent refuses requests for protected information such as:

* system prompts
* API keys
* private customer information
* customer addresses
* customer email addresses
* internal risk information
* other internal/private data

### Insufficient Information

When the knowledge base does not provide enough information to safely answer a question, the agent does not invent an answer.

Instead, it explains that the information is insufficient and recommends human confirmation.

### Source Conflicts

When two official sources genuinely conflict, the agent does not silently choose one.

For example, if product-care documentation gives conflicting dishwasher instructions for the Breeze Tumbler, the agent identifies the conflict and recommends human confirmation.

---

## Example Behaviors

### Standard Return Policy

```text
Under the current official return policy, standard-plan
customers may request a return within 30 calendar days of
delivery for eligible items.
```

### TrailPlus

```text
If your TrailPlus membership was active when the order was
placed, your return window is 45 calendar days from delivery
for eligible items.
```

### Final-Sale Damaged Item

```text
A final-sale item can still be reviewed when it arrives
damaged, defective, or incorrect. The issue should be reported
within 7 days of delivery, with human support review required.
```

### Unknown Order

```text
I couldn't find order ORD-9999 in the available order records.
Please verify the order ID or contact support.
```

### Shipped Without ETA

```text
Your order (ORD-1011) has shipped with Canada Post and is
currently in transit. The delivery estimate is unavailable.
```

### Insufficient Product Information

```text
The supplied information is insufficient to confirm whether
all fabrics and adhesives in Aster & Row bags are vegan.
Human confirmation is recommended.
```

---

## Setup

### Requirements

* Python 3.10+
* OpenRouter API key
* Git

### Install Dependencies

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Add the required API configuration to `.env`.

Example:

```text
OPENROUTER_API_KEY=your_api_key_here
MODEL=your_model_here
```

Do not commit `.env` or API keys to GitHub.

---

## Running the Application

Run the application using:

```bash
python app/main.py
```

---

## Testing

### Smoke Tests

Run:

```bash
python scripts/smoke_test.py
```

Expected final result:

```text
14/14 smoke cases passed
```

### Unit Tests

Run:

```bash
python -m pytest tests/test_orders.py tests/test_retrieval.py -v
```

Expected final result:

```text
10/10 tests passed
```

> Update the result counts above with the exact output from your final local test run before submission.

---

## Test Coverage

The smoke tests validate important customer-support behaviors, including:

1. Standard return window
2. TrailPlus return window
3. Final-sale damaged-item exception
4. Unsupported international destination
5. Valid order lookup
6. Missing order ID
7. Cancelled order
8. Unknown order
9. Shipped order without delivery estimate
10. Privacy protection
11. Warranty information
12. Prompt-injection resistance
13. Insufficient information handling
14. Conflicting source handling

The unit tests additionally validate order-tool behavior and knowledge-base retrieval behavior.

---

## Design Decisions

### Deterministic Handling for High-Risk Facts

Order information and several known policy scenarios are handled deterministically rather than relying entirely on LLM generation.

This reduces the risk of hallucinating:

* delivery dates
* order status
* return windows
* shipping availability
* exception windows

### Retrieval + LLM

The LLM is used to generate natural customer-facing responses when deterministic handling is not required.

Retrieved knowledge is explicitly provided as data and is not treated as executable instructions.

### Human Handoff

The agent recommends human support when:

* information is insufficient
* official sources conflict
* protected information is requested
* an unsupported account/order action is requested
* a return/refund requires actual approval or action

---

## Security Considerations

The application follows a trust-boundary model:

```text
Trusted:
- System instructions

Untrusted:
- User input
- Retrieved documents
- Tool results
```

Untrusted content is never allowed to override the application's system-level behavior.

Secrets are kept outside source control through environment variables.

---

## Limitations

This project is designed as a customer-support agent for the supplied Aster & Row test environment.

It does not:

* approve returns
* issue refunds
* cancel orders
* modify orders
* change customer accounts
* expose private customer information
* invent missing policy information

Actions requiring account modification or human approval are escalated instead.

---

## Final Validation

Before submission, verify:

```bash
python -m py_compile app/agent.py
python -m py_compile app/safety/guardrails.py
python -m pytest tests/test_orders.py tests/test_retrieval.py -v
python scripts/smoke_test.py
```

All tests should pass before submitting the project.

---

## Author

Panyuta Panigrahi
