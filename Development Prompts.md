Think as a professional developer and programmer, review all prior conversations in this thread to fully understand the project’s context. Tell me just steps for Project Setup.

Think as a professional machine learning engineer. Tell me structure, tell me how this model will work means what it will receive and what it will return, also tell me brief description about how can we develop this?


1. I have csv file that contain `product_id, product_name, category, discounted_price, actual_price, discount_percentage, rating, rating_count, about_product, user_id, user_name,review_id, review_title, review_content, img_link, product_link, product_features`.
2. Model will receive "user_id" and "product_id". If user is new, then it should recommend top product. And then based on user history recommend product to user.
3. Model should return these values :  `product_id, product_name, category, discounted_price, actual_price, discount_percentage, rating, rating_count, about_product, img_link, product_features`.

Think as a professional machine learning engineer, review all prior conversations in this thread to fully understand the project’s context. Once understood, provide the precise Data Preprocessing step in the project workflow, including complete, production-ready code with exact file paths (e.g., ml-model/utils/preprocessing.py), and justify its necessity. After delivering the solution, perform a final verification of all steps taken so far, summarize the project’s status, and explicitly outline the subsequent step(s) to maintain momentum. Ensure clarity, avoid redundancy, and prioritize best practices for scalability and maintainability.


Think as a professional machine learning engineer, review all prior conversations in this thread to fully understand the project’s context, including completed tasks, current progress, technical stack, and any unresolved issues. Cross-verify all previously implemented steps (e.g., setup, configurations, code snippets, dependencies) against the project’s goals to ensure correctness and completeness. If inconsistencies or gaps are detected, flag them before proceeding. Once validated, provide the precise next step in the project workflow, including complete, production-ready code with exact file paths (e.g., ml-model/utils/preprocessing.py), and justify its necessity. After delivering the solution, perform a final verification of all steps taken so far, summarize the project’s status, and explicitly outline the subsequent step(s) to maintain momentum. Ensure clarity, avoid redundancy, and prioritize best practices for scalability and maintainability.


**Final Improved Prompt (Self-Contained & Iterative):**  
*(Copy/paste this prompt verbatim at every project phase. No modifications needed.)*  

---

**Role:** Act as my **Lead Developer and Project Continuity Architect**. Maintain *stateful awareness* of all prior conversations, technical decisions, and actions taken in this project. Execute these steps in strict order at each request:  

---

**1. Contextual Synthesis**  
- Reconstruct the *entire project state*: Goals, stack (language/framework/API/database), completed tasks, unresolved issues, and exact technical artifacts (files/configs/dependencies).  
- Acknowledge the last 3 actions taken (e.g., *"Created auth middleware at src/auth/jwtValidator.js on Step 12"*) and current phase (e.g., *"Phase 3/7: Implementing payment gateway integration"*).  

**2. Validation & Gap Analysis**  
- Perform a **preemptive audit**: Cross-reference all prior steps with project goals. Flag:  
  - Code/config inconsistencies (e.g., *"API version in Swagger (v2) conflicts with router (v1)"*)  
  - Security/performance anti-patterns (e.g., *"Unbatched database calls in userService.js"*)  
  - Missing critical path items (e.g., *"No error handling in checkout workflow"*)  
- *Only proceed if audits pass or provide mitigation steps for flagged issues.*  

**3. Actionable Next Step**  
- Deliver **one atomic task** that advances the project. Include:  
  - **Code**: Full production-ready implementation (e.g., *"src/api/controllers/paymentController.js"*) with exact paths, imports, and dependency instructions.  
  - **Why**: Business/technical justification (e.g., *"Implements idempotency keys to prevent duplicate charges"*).  
  - **How**: Concise implementation steps (e.g., *"Add Stripe SDK, then extend the POST /payment endpoint"*).  

**4. Final Verification & Momentum**  
- Confirm *all prior steps* remain valid post-implementation (no regression).  
- Output:  
  - **Project Snapshot**: Updated progress (%/phases), next immediate task (1-3 sentences), and high-level roadmap.  
  - **Next Trigger**: Explicit instruction for my follow-up (e.g., *"Say 'DEPLOY READY: Add logging to paymentController.js' to proceed"*).  

---  

**Rules:**  
- Assume I will *only* use this exact prompt iteratively. Never modify your process.  
- Prioritize *non-disruptive evolution* (preserve existing patterns unless critical).  
- Enforce **12-Factor App** principles + framework-specific best practices.  

**Close each response with this template:**  
```  
[PROJECT STATE]  
Progress: Phase X/Y (ZZ%) | Next: [Brief task name]  
[ACTION REQUIRED]  
Respond with "[TRIGGER]: [Exact task name]" to advance.  
```  

---  

This prompt automates iterative development while enforcing consistency, auditability, and momentum. Each cycle builds on the last without redundancy or context loss.