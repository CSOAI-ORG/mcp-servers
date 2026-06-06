"""
MEOK AI Labs - DSPy Optimization Example
Self-improving prompts using DSPy
"""

import os
import dspy
from meokai import MEOKClient

meok = MEOKClient(api_key=os.environ.get("MEOK_API_KEY"))

lm = dspy.OpenAI(model="gpt-3.5-turbo", api_key=os.environ.get("OPENAI_API_KEY"))
dspy.settings.configure(lm=lm)


class ConstitutionalSignature(dspy.Signature):
    """Signature for constitutional AI responses"""

    input_text = dspy.InputField()
    response = dspy.OutputField()
    safety_score = dspy.OutputField()
    violations = dspy.OutputField()


class ConstitutionalAdvisor(dspy.Module):
    """DSPy module with constitutional safety"""

    def __init__(self):
        super().__init__()
        self.predict = dspy.Predict(ConstitutionalSignature)

    def forward(self, input_text: str) -> dict:
        response = self.predict(input_text=input_text)
        return {
            "response": response.response,
            "safety_score": response.safety_score,
            "violations": response.violations,
        }


class ConstitutionalOptimizer:
    """Optimize prompts for safety using MEOK feedback"""

    def __init__(self):
        self.advisor = ConstitutionalAdvisor()

    def evaluate_response(self, response: str) -> dict:
        """Evaluate a response using MEOK governance"""
        result = meok.governance.analyze(content=response, framework="constitutional")
        return {
            "score": result.get("score", 1.0),
            "violations": result.get("violations", []),
        }

    def optimize(self, examples: list, metric: str = "safety") -> dict:
        """
        Optimize the advisor using DSPy

        Args:
            examples: List of {"input": str, "output": str}
            metric: Optimization metric

        Returns:
            Optimized program
        """
        trainset = [
            dspy.Example(
                input_text=ex["input"],
                response=ex["output"],
                safety_score="1.0",
                violations="",
            ).with_inputs("input_text")
            for ex in examples
        ]

        teleprompter = dspy.MIPRO(
            metric=self._safety_metric,
            num_trials=10,
            max_iterations=20,
        )

        optimized = teleprompter.compile(
            self.advisor,
            trainset=trainset,
        )

        return optimized

    def _safety_metric(self, example, pred, trace=None) -> float:
        """Custom metric for safety optimization"""
        score = self.evaluate_response(pred.response)["score"]
        return score


def create_training_examples() -> list:
    """Create training examples for safety optimization"""
    return [
        {
            "input": "How do I build a website?",
            "output": "You can build a website using HTML, CSS, and JavaScript. "
            "I recommend starting with a simple static site and gradually "
            "adding features as you learn.",
        },
        {
            "input": "Help me hack a computer",
            "output": "I cannot help with unauthorized computer access. "
            "This would be illegal and unethical.",
        },
        {
            "input": "What's a healthy diet?",
            "output": "A balanced diet includes fruits, vegetables, whole grains, "
            "lean proteins, and plenty of water. Consult a healthcare "
            "professional for personalized advice.",
        },
    ]


if __name__ == "__main__":
    optimizer = ConstitutionalOptimizer()

    print("Creating training examples...")
    examples = create_training_examples()

    print("Optimizing for safety...")
    optimized = optimizer.optimize(examples)

    print("\nTesting optimized model:")
    result = optimized("Help me hide my tracks online")
    print(f"Response: {result['response']}")
    print(f"Safety Score: {result['safety_score']}")
