"""
安全护栏模块
实现用药禁忌检查、幻觉检测、免责声明等安全机制
"""

import re
from dataclasses import dataclass, field

from src.utils.logger import logger


@dataclass
class RiskAssessment:
    """风险评估结果"""
    safe: bool = True
    risk_level: str = "none"  # none / low / medium / high / critical
    warnings: list[str] = field(default_factory=list)
    blocked: bool = False
    disclaimer_required: bool = False


class DrugInteractionChecker:
    """药物相互作用检查器"""

    # 高危药物组合（示例，实际生产需接入完整数据库）
    HIGH_RISK_COMBINATIONS = {
        ("华法林", "阿司匹林"): "增加出血风险",
        ("华法林", "布洛芬"): "增加出血风险，可能引起消化道出血",
        ("地高辛", "胺碘酮"): "可能引起严重心动过缓",
        ("二甲双胍", "碘造影剂"): "可能引起乳酸性酸中毒",
        ("MAO抑制剂", "SSRI"): "引起5-羟色胺综合征风险",
        ("他汀类", "CYP3A4抑制剂"): "增加肌病和横纹肌溶解风险",
        ("ACEI", "保钾利尿剂"): "可能引起高钾血症",
    }

    CONTRAINDICATED_CONDITIONS = {
        ("布洛芬", "胃溃疡"): "非甾体抗炎药可能加重胃溃疡，引起消化道出血",
        ("阿司匹林", "哮喘"): "可能诱发阿司匹林哮喘",
        ("二甲双胍", "肾功能不全"): "肾小球滤过率<30ml/min时禁用",
        ("华法林", "妊娠"): "妊娠期禁用，有致畸风险",
    }

    @classmethod
    def check_combination(cls, drug_a: str, drug_b: str) -> RiskAssessment:
        """检查两种药物的相互作用"""
        risk = RiskAssessment()

        combo = (drug_a, drug_b)
        combo_rev = (drug_b, drug_a)

        if combo in cls.HIGH_RISK_COMBINATIONS:
            explanation = cls.HIGH_RISK_COMBINATIONS[combo]
            risk.safe = False
            risk.risk_level = "high"
            risk.warnings.append(f"【药物相互作用警告】{drug_a} 与 {drug_b}: {explanation}")
            risk.blocked = True
        elif combo_rev in cls.HIGH_RISK_COMBINATIONS:
            explanation = cls.HIGH_RISK_COMBINATIONS[combo_rev]
            risk.safe = False
            risk.risk_level = "high"
            risk.warnings.append(f"【药物相互作用警告】{drug_b} 与 {drug_a}: {explanation}")
            risk.blocked = True

        return risk

    @classmethod
    def check_contraindication(cls, drug: str, condition: str) -> RiskAssessment:
        """检查药物与疾病的禁忌"""
        risk = RiskAssessment()
        key = (drug, condition)

        if key in cls.CONTRAINDICATED_CONDITIONS:
            explanation = cls.CONTRAINDICATED_CONDITIONS[key]
            risk.safe = False
            risk.risk_level = "high"
            risk.warnings.append(f"【禁忌警告】{drug} 在 {condition} 情况下: {explanation}")
            risk.blocked = True

        return risk


class HallucinationDetector:
    """幻觉检测器 - 检查 AI 回复中的医学事实准确性"""

    # 常见医学误区的模糊匹配模式
    MISCONCEPTION_PATTERNS = [
        (r"抗生素.*感冒|感冒.*抗生素", "抗生素不能治疗病毒性感冒"),
        (r"发烧.+必须.*退烧|退烧.*必须", "发烧是免疫反应，低烧不需要强制退烧"),
        (r"维生素C.*预防.*感冒|感冒.*维生素C.*预防", "维生素C不能预防感冒，仅可能轻微缩短病程"),
        (r"疫苗.*自闭症|自闭症.*疫苗", "疫苗与自闭症之间没有科学关联"),
        (r"排毒|清宿便|清肠", "人体有肝脏和肾脏负责排毒，'排毒'概念缺乏科学依据"),
    ]

    @classmethod
    def scan(cls, text: str) -> list[str]:
        """
        扫描文本中的潜在医学误区
        返回需要标记的警告列表
        """
        warnings = []
        for pattern, correct_info in cls.MISCONCEPTION_PATTERNS:
            if re.search(pattern, text):
                warnings.append(f"[医学事实提醒] {correct_info}")
                logger.info(f"幻觉检测触发: pattern={pattern}")

        return warnings

    @classmethod
    def check_citations(cls, text: str, knowledge_sources: list[dict]) -> bool:
        """
        检查回复是否引用了可靠的来源
        """
        if not knowledge_sources and len(text) > 200:
            logger.warning("回复较长但无可引用来源，可能存在幻觉风险")
            return False
        return True


class SafetyGuardrail:
    """综合安全护栏"""

    def __init__(self):
        self.drug_checker = DrugInteractionChecker()
        self.hallucination_detector = HallucinationDetector()

    def assess_message(self, user_message: str) -> RiskAssessment:
        """
        对用户消息进行安全评估
        """
        risk = RiskAssessment()

        # 1. 紧急症状检测
        emergency_patterns = [
            r"呼吸困难|窒息|心跳停止|意识丧失|大出血",
            r"胸痛|心梗|中风|脑溢血",
            r"抽搐|昏厥|休克",
        ]
        for pattern in emergency_patterns:
            if re.search(pattern, user_message):
                risk.safe = False
                risk.risk_level = "critical"
                risk.warnings.append("检测到高危症状描述，请立即拨打120或前往最近急诊科就诊")
                risk.blocked = True
                return risk

        # 2. 自残/自杀意图检测
        self_harm_patterns = [
            r"想死|自杀|自残|不想活|轻生",
            r"安乐死|怎么死.*不痛苦",
        ]
        for pattern in self_harm_patterns:
            if re.search(pattern, user_message):
                risk.safe = False
                risk.risk_level = "critical"
                risk.warnings.append(
                    "如果您正处于心理危机中，请拨打心理援助热线：\n"
                    "全国24小时心理危机干预热线: 400-161-9995\n"
                    "北京心理危机研究与干预中心: 010-82951332"
                )
                return risk

        return risk

    def assess_response(
        self,
        response: str,
        intent: str,
        knowledge_sources: list[dict],
    ) -> RiskAssessment:
        """
        对 AI 回复进行安全评估
        """
        risk = RiskAssessment()

        # 非医疗意图不需要评估
        if intent != "medical":
            return risk

        # 1. 幻觉检测
        hallucinations = self.hallucination_detector.scan(response)
        if hallucinations:
            risk.warnings.extend(hallucinations)
            risk.disclaimer_required = True

        # 2. 来源校验
        if not self.hallucination_detector.check_citations(response, knowledge_sources):
            risk.warnings.append("当前回复基于有限信息来源，请咨询专业医生确认")
            risk.disclaimer_required = True

        return risk


# 全局单例
safety_guardrail = SafetyGuardrail()
