# AI Governance Assessment Questionnaire

This questionnaire assesses AI use cases from IT Security, Data Privacy, EU AI Act, and AI Ethics perspectives.

---

## Section 1: General Information

### Q1.1 - Use Case Name
**Question:** What is the name of the AI use case you want to assess?
**Type:** text
**Required:** true

### Q1.2 - Use Case Description
**Question:** Please provide a detailed description of the AI use case, including its purpose and intended functionality.
**Type:** text
**Required:** true

### Q1.3 - Business Owner
**Question:** Who is the business owner responsible for this AI use case?
**Type:** text
**Required:** true

### Q1.4 - Technical Owner
**Question:** Who is the technical owner responsible for implementing and maintaining this AI system?
**Type:** text
**Required:** true

### Q1.5 - Target Users
**Question:** Who are the intended users of this AI system? (e.g., internal employees, customers, partners)
**Type:** text
**Required:** true

---

## Section 2: IT Security

### Q2.1 - Data Classification
**Question:** What is the classification level of the data processed by this AI system?
**Options:** Public, Internal, Confidential, Strictly Confidential
**Type:** choice
**Required:** true

### Q2.2 - Data Sources
**Question:** What are the data sources for this AI system? Please list all internal and external data sources.
**Type:** text
**Required:** true

### Q2.3 - Authentication Requirements
**Question:** What authentication mechanisms will be used to access the AI system?
**Options:** SSO/Corporate Identity, API Keys, OAuth 2.0, No Authentication Required, Other
**Type:** choice
**Required:** true

### Q2.4 - Network Security
**Question:** Will the AI system be deployed in a segmented network environment? Describe the network architecture.
**Type:** text
**Required:** true

### Q2.5 - Third-Party Components
**Question:** Does the AI system use third-party components, libraries, or external APIs? If yes, please list them.
**Type:** text
**Required:** true

### Q2.6 - Vulnerability Assessment
**Question:** Has a security vulnerability assessment been conducted for this AI system?
**Options:** Yes - completed, Yes - in progress, Planned, Not yet planned
**Type:** choice
**Required:** true

### Q2.7 - Incident Response
**Question:** Is there an incident response plan specific to this AI system? Describe how security incidents will be handled.
**Type:** text
**Required:** true

---

## Section 3: Data Privacy (GDPR)

### Q3.1 - Personal Data Processing
**Question:** Does the AI system process personal data (any information relating to an identified or identifiable natural person)?
**Options:** Yes, No, Uncertain
**Type:** choice
**Required:** true

### Q3.2 - Special Category Data
**Question:** Does the AI system process special category data (e.g., health data, biometric data, racial/ethnic origin, political opinions)?
**Options:** Yes, No, Uncertain
**Type:** choice
**Required:** true

### Q3.3 - Legal Basis
**Question:** What is the legal basis for processing personal data?
**Options:** Consent, Contract, Legal Obligation, Vital Interests, Public Task, Legitimate Interests, Not Applicable
**Type:** choice
**Required:** true

### Q3.4 - Data Subjects
**Question:** Who are the data subjects whose personal data will be processed?
**Type:** text
**Required:** true

### Q3.5 - Data Retention
**Question:** What is the data retention period for personal data processed by this AI system?
**Type:** text
**Required:** true

### Q3.6 - Data Subject Rights
**Question:** How will data subject rights be facilitated (access, rectification, erasure, portability, objection)?
**Type:** text
**Required:** true

### Q3.7 - International Transfers
**Question:** Will personal data be transferred outside the EU/EEA? If yes, what safeguards are in place?
**Type:** text
**Required:** true

### Q3.8 - DPIA Required
**Question:** Has a Data Protection Impact Assessment (DPIA) been conducted or is one planned?
**Options:** Yes - completed, Yes - in progress, Planned, Not required, Uncertain
**Type:** choice
**Required:** true

### Q3.9 - Privacy by Design
**Question:** What privacy-by-design measures have been implemented in this AI system?
**Type:** text
**Required:** true

---

## Section 4: EU AI Act Compliance

### Q4.1 - AI System Classification
**Question:** Based on the EU AI Act, how would you classify this AI system?
**Options:** Minimal Risk, Limited Risk (Transparency), High Risk, Unacceptable Risk, Uncertain
**Type:** choice
**Required:** true

### Q4.2 - High-Risk Category
**Question:** If classified as High Risk, which category does it fall under? (e.g., biometric identification, critical infrastructure, education, employment, essential services, law enforcement, migration/border control)
**Type:** text
**Required:** false

### Q4.3 - Human Oversight
**Question:** What human oversight mechanisms are in place for this AI system?
**Type:** text
**Required:** true

### Q4.4 - Transparency Measures
**Question:** How will users be informed that they are interacting with an AI system?
**Type:** text
**Required:** true

### Q4.5 - Technical Documentation
**Question:** Is comprehensive technical documentation available for this AI system?
**Options:** Yes - complete, Yes - partial, In progress, Not yet started
**Type:** choice
**Required:** true

### Q4.6 - Risk Management
**Question:** Describe the risk management system in place for this AI system.
**Type:** text
**Required:** true

### Q4.7 - Data Governance
**Question:** What data governance practices are implemented for training, validation, and testing datasets?
**Type:** text
**Required:** true

### Q4.8 - Accuracy and Robustness
**Question:** What measures ensure the accuracy, robustness, and cybersecurity of the AI system?
**Type:** text
**Required:** true

### Q4.9 - Record Keeping
**Question:** How will logs and records be maintained for this AI system (as required by EU AI Act)?
**Type:** text
**Required:** true

---

## Section 5: AI Ethics

### Q5.1 - Fairness Assessment
**Question:** How has the AI system been assessed for fairness and bias?
**Type:** text
**Required:** true

### Q5.2 - Protected Groups
**Question:** Which protected groups might be affected by this AI system, and how are their interests safeguarded?
**Type:** text
**Required:** true

### Q5.3 - Explainability
**Question:** Can the AI system's decisions be explained to affected individuals? Describe the explainability approach.
**Type:** text
**Required:** true

### Q5.4 - Accountability
**Question:** Who is accountable for the AI system's decisions and their consequences?
**Type:** text
**Required:** true

### Q5.5 - Environmental Impact
**Question:** What is the estimated environmental impact of training and operating this AI system?
**Type:** text
**Required:** true

### Q5.6 - Societal Impact
**Question:** What broader societal impacts (positive and negative) might this AI system have?
**Type:** text
**Required:** true

### Q5.7 - Appeal Mechanism
**Question:** Is there a mechanism for individuals to appeal or contest AI-driven decisions?
**Type:** text
**Required:** true

### Q5.8 - Ethical Review
**Question:** Has this AI use case undergone an ethical review process?
**Options:** Yes - approved, Yes - pending, Planned, Not required, Not yet initiated
**Type:** choice
**Required:** true

---

## Section 6: Implementation and Monitoring

### Q6.1 - Go-Live Date
**Question:** What is the planned go-live date for this AI system?
**Type:** text
**Required:** true

### Q6.2 - Monitoring Plan
**Question:** Describe the ongoing monitoring plan for this AI system post-deployment.
**Type:** text
**Required:** true

### Q6.3 - Review Frequency
**Question:** How often will this AI governance assessment be reviewed and updated?
**Options:** Quarterly, Semi-annually, Annually, Upon significant changes, Other
**Type:** choice
**Required:** true

### Q6.4 - Additional Comments
**Question:** Are there any additional comments, concerns, or information relevant to this AI governance assessment?
**Type:** text
**Required:** false

---

*End of Questionnaire*
