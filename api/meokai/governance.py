"""
MEOK AI Labs - Constitutional AI Governance
"""

from typing import Dict, List, Any
import hashlib


class ConstitutionalAnalyzer:
    """Analyze content against Constitutional AI principles"""

    PRINCIPLES = [
        "Helpfulness without harm",
        "Respect for autonomy",
        "Privacy protection",
        "Fairness and non-discrimination",
        "Transparency and explainability",
        "Accountability",
        "Safety and security",
    ]

    VIOLATION_TYPES = {
        "harmful_content": {
            "severity": "high",
            "description": "Content that could cause harm",
        },
        "hate_speech": {
            "severity": "high",
            "description": "Discriminatory or hateful content",
        },
        "misinformation": {
            "severity": "medium",
            "description": "False or misleading information",
        },
        "privacy_violation": {
            "severity": "high",
            "description": "Personal data concerns",
        },
        "self_harm": {"severity": "critical", "description": "Self-harm encouragement"},
        "violence": {
            "severity": "critical",
            "description": "Violent content or instructions",
        },
        "illegal_content": {
            "severity": "critical",
            "description": "Illegal activity instructions",
        },
    }

    def __init__(self):
        self.cache = {}

    async def analyze(
        self,
        content: str,
        framework: str = "constitutional",
        content_type: str = "text",
    ) -> Dict[str, Any]:
        """Analyze content and return safety assessment"""
        content_hash = hashlib.sha256(content.encode()).hexdigest()

        if content_hash in self.cache:
            return self.cache[content_hash]

        violations = self._detect_violations(content)
        score = self._calculate_score(violations)

        result = {
            "content_hash": content_hash,
            "score": score,
            "passed": score >= 0.7,
            "violations": violations,
            "recommendations": self._generate_recommendations(violations),
            "framework": framework,
        }

        self.cache[content_hash] = result
        return result

    def _detect_violations(self, content: str) -> List[Dict]:
        """Detect policy violations in content"""
        violations = []
        content_lower = content.lower()

        harmful_patterns = {
            "harmful_content": ["how to hurt", "how to kill", "how to attack"],
            "hate_speech": ["hate", "slur", "discriminate"],
            "misinformation": ["fake news", "conspiracy"],
            "privacy_violation": ["steal identity", "hack account"],
            "self_harm": ["suicide", "self-harm", "cut myself"],
            "violence": ["weapon", "bomb", "explosive"],
            "illegal_content": ["drugs", "fraud", "theft"],
        }

        for violation_type, patterns in harmful_patterns.items():
            for pattern in patterns:
                if pattern in content_lower:
                    violations.append(
                        {
                            "type": violation_type,
                            "severity": self.VIOLATION_TYPES[violation_type][
                                "severity"
                            ],
                            "description": self.VIOLATION_TYPES[violation_type][
                                "description"
                            ],
                            "matched_pattern": pattern,
                        }
                    )
                    break

        return violations

    def _calculate_score(self, violations: List[Dict]) -> float:
        """Calculate safety score based on violations"""
        if not violations:
            return 1.0

        severity_weights = {
            "critical": 0.4,
            "high": 0.25,
            "medium": 0.15,
            "low": 0.05,
        }

        penalty = sum(
            severity_weights.get(v.get("severity", "low"), 0.1) for v in violations
        )

        return max(0.0, 1.0 - penalty)

    def _generate_recommendations(self, violations: List[Dict]) -> List[str]:
        """Generate recommendations based on violations"""
        recommendations = []

        violation_types = {v["type"] for v in violations}

        if "harmful_content" in violation_types:
            recommendations.append(
                "Consider reframing the request to focus on a constructive goal"
            )

        if "hate_speech" in violation_types:
            recommendations.append("Ensure all content promotes respect and equality")

        if "misinformation" in violation_types:
            recommendations.append(
                "Verify information from reliable sources before sharing"
            )

        if "privacy_violation" in violation_types:
            recommendations.append("Do not share or request personal information")

        if "self_harm" in violation_types:
            recommendations.append(
                "If you're experiencing thoughts of self-harm, please seek support"
            )

        if "violence" in violation_types:
            recommendations.append(
                "Consider peaceful alternatives to resolve conflicts"
            )

        if "illegal_content" in violation_types:
            recommendations.append("Ensure all activities comply with applicable laws")

        if not recommendations:
            recommendations.append("Content appears safe")

        return recommendations

    async def check_compliance(
        self,
        content: str,
        standards: List[str],
    ) -> Dict[str, Any]:
        """Check compliance against multiple standards"""
        results = {}

        for standard in standards:
            analysis = await self.analyze(content, framework=standard)
            results[standard] = {
                "passed": analysis["passed"],
                "score": analysis["score"],
                "violations": analysis["violations"],
            }

        return {
            "overall_passed": all(r["passed"] for r in results.values()),
            "results": results,
        }
