Dear Team,

I am Pranav Yadav, an MSc student at the University of Bonn. I am writing regarding your paper, "Automated Researchers Can Mitigate Well-Characterized Alignment Failures." Your finding that automated techniques can successfully mitigate alignment failures directly aligns with our project’s focus on identifying the specific attention heads that causally produce refusal in small instruct LLMs.

We are currently investigating whether retraining only these identified heads via LoRA editing can replicate the mitigation effects you observed. Specifically, our preliminary findings indicate that training heads on benign data alone can transfer to harmful prompts in robustly-aligned models like Llama-3.2-3B, achieving significant substantive-ASR increases without harmful training data.

Given your results on automated mitigation, could you clarify if your automated researchers identified specific architectural components, such as attention heads, as the primary drivers of this mitigation, or did the method operate on broader model parameters?

Best regards,

Pranav Yadav