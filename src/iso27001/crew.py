from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

from iso27001.tools import ISOKnowledgeRetriever
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class Iso27001():
    """Iso27001 crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    knowledge_tool = ISOKnowledgeRetriever()

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def iso27001_consultant_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['iso27001_consultant_agent'], # type: ignore[index]
            tools=[self.knowledge_tool],
            verbose=True
        )

    @agent
    def asset_inventory_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['asset_inventory_agent'], # type: ignore[index]
            verbose=True
        )

    @agent
    def risk_assessment_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['risk_assessment_agent'], # type: ignore[index]
            tools=[self.knowledge_tool],
            verbose=True
        )

    @agent
    def risk_treatment_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['risk_treatment_agent'], # type: ignore[index]
            tools=[self.knowledge_tool],
            verbose=True
        )

    @agent
    def policy_writer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['policy_writer_agent'], # type: ignore[index]
            tools=[self.knowledge_tool],
            verbose=True
        )

    @agent
    def compliance_auditor_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['compliance_auditor_agent'], # type: ignore[index]
            tools=[self.knowledge_tool],
            verbose=True
        )

    @agent
    def documentation_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['documentation_agent'], # type: ignore[index]
            verbose=True
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def determine_context_task(self) -> Task:
        return Task(
            config=self.tasks_config['determine_context_task'], # type: ignore[index]
        )

    @task
    def identify_interested_parties_task(self) -> Task:
        return Task(
            config=self.tasks_config['identify_interested_parties_task'], # type: ignore[index]
        )

    @task
    def define_scope_task(self) -> Task:
        return Task(
            config=self.tasks_config['define_scope_task'], # type: ignore[index]
        )

    @task
    def establish_processes_task(self) -> Task:
        return Task(
            config=self.tasks_config['establish_processes_task'], # type: ignore[index]
        )

    @task
    def identify_information_assets_task(self) -> Task:
        return Task(
            config=self.tasks_config['identify_information_assets_task'], # type: ignore[index]
        )

    @task
    def identify_supporting_assets_task(self) -> Task:
        return Task(
            config=self.tasks_config['identify_supporting_assets_task'], # type: ignore[index]
        )

    @task
    def assign_asset_owners_task(self) -> Task:
        return Task(
            config=self.tasks_config['assign_asset_owners_task'], # type: ignore[index]
        )

    @task
    def classify_assets_task(self) -> Task:
        return Task(
            config=self.tasks_config['classify_assets_task'], # type: ignore[index]
        )

    @task
    def define_risk_assessment_criteria_task(self) -> Task:
        return Task(
            config=self.tasks_config['define_risk_assessment_criteria_task'], # type: ignore[index]
        )

    @task
    def identify_threats_task(self) -> Task:
        return Task(
            config=self.tasks_config['identify_threats_task'], # type: ignore[index]
        )

    @task
    def identify_vulnerabilities_task(self) -> Task:
        return Task(
            config=self.tasks_config['identify_vulnerabilities_task'], # type: ignore[index]
        )

    @task
    def calculate_likelihood_impact_task(self) -> Task:
        return Task(
            config=self.tasks_config['calculate_likelihood_impact_task'], # type: ignore[index]
        )

    @task
    def generate_risk_register_task(self) -> Task:
        return Task(
            config=self.tasks_config['generate_risk_register_task'], # type: ignore[index]
        )

    @task
    def evaluate_risks_task(self) -> Task:
        return Task(
            config=self.tasks_config['evaluate_risks_task'], # type: ignore[index]
        )

    @task
    def decide_treatment_strategy_task(self) -> Task:
        return Task(
            config=self.tasks_config['decide_treatment_strategy_task'], # type: ignore[index]
        )

    @task
    def map_risks_to_controls_task(self) -> Task:
        return Task(
            config=self.tasks_config['map_risks_to_controls_task'], # type: ignore[index]
        )

    @task
    def generate_risk_treatment_plan_task(self) -> Task:
        return Task(
            config=self.tasks_config['generate_risk_treatment_plan_task'], # type: ignore[index]
        )

    @task
    def generate_policies_task(self) -> Task:
        return Task(
            config=self.tasks_config['generate_policies_task'], # type: ignore[index]
        )

    @task
    def align_policies_with_risk_treatment_task(self) -> Task:
        return Task(
            config=self.tasks_config['align_policies_with_risk_treatment_task'], # type: ignore[index]
        )

    @task
    def ensure_policy_compliance_task(self) -> Task:
        return Task(
            config=self.tasks_config['ensure_policy_compliance_task'], # type: ignore[index]
        )

    @task
    def evaluate_controls_task(self) -> Task:
        return Task(
            config=self.tasks_config['evaluate_controls_task'], # type: ignore[index]
        )

    @task
    def determine_control_applicability_task(self) -> Task:
        return Task(
            config=self.tasks_config['determine_control_applicability_task'], # type: ignore[index]
        )

    @task
    def generate_statement_of_applicability_task(self) -> Task:
        return Task(
            config=self.tasks_config['generate_statement_of_applicability_task'], # type: ignore[index]
        )

    @task
    def identify_missing_controls_task(self) -> Task:
        return Task(
            config=self.tasks_config['identify_missing_controls_task'], # type: ignore[index]
        )

    @task
    def collect_agent_outputs_task(self) -> Task:
        return Task(
            config=self.tasks_config['collect_agent_outputs_task'], # type: ignore[index]
        )

    @task
    def generate_final_documentation_task(self) -> Task:
        return Task(
            config=self.tasks_config['generate_final_documentation_task'], # type: ignore[index]
        )

    @task
    def ensure_audit_ready_task(self) -> Task:
        return Task(
            config=self.tasks_config['ensure_audit_ready_task'], # type: ignore[index]
        )

    @task
    def readiness_review_task(self) -> Task:
        return Task(
            config=self.tasks_config['readiness_review_task'], # type: ignore[index]
            output_file='outputs/iso27001_readiness_report.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Iso27001 crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
