import chainlit as cl
from chainlit.input_widget import Select
from langgraph.graph import StateGraph
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable, RunnableConfig
from langgraph.prebuilt import ToolNode

from .base import BaseWorkflow, BaseState
from ..llm import llm_factory, ModelCapability
from ..tools.opensearch_vectorstore import vector_retriever
from ..tools.plot import (
        plot_bar_chart,
        plot_pie_chart,
        plot_line_chart,
        plot_bubble_chart)


class GraphState(BaseState):
    # Model name of the chatbot
    chat_model: str


class DataScienceWorkflow(BaseWorkflow):
    def __init__(self):
        super().__init__()

        self.capabilities = {ModelCapability.TEXT_TO_TEXT, ModelCapability.TOOL_CALLING}
        self.tools = [vector_retriever, plot_bar_chart, plot_pie_chart, plot_line_chart, plot_bubble_chart]

    def create_graph(self) -> StateGraph:
        graph = StateGraph(GraphState)
        graph.add_node("chat", self.chat_node)
        graph.add_node("tools", ToolNode(self.tools))

        # TODO: create a router for using multiple tools
        graph.set_entry_point("chat")
        graph.add_conditional_edges("chat", self.tool_routing)
        graph.add_edge("tools", "chat")
        return graph

    async def chat_node(self, state: GraphState, config: RunnableConfig) -> GraphState:
        prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content="""
                    System: You are an agent designed to interact with a SQL database.\n
                    Given an input question, create a syntactically correct ElasticSearchSQL
                    and HiveQL query to run, then look at the results of the query and return the
                    answer.\nUnless the user specifies a specific number of examples they wish to
                    obtain, always limit your query to at most 5 results.\nYou can order the results
                    by a relevant column to return the most interesting examples in the database.
                    \nNever query for all the columns from a specific table, only ask for the relevant
                    columns given the question.\nYou have access to tools for interacting with the
                    database.\nOnly use the below tools. Only use the information returned by the below
                    tools to construct your final answer.\nYou MUST double check your query before
                    executing it. If you get an error while executing a query, rewrite the query and try
                    again.\n\nDO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the
                    database.\n\nTo start you should ALWAYS look at the tables in the database to see what
                    you can query.\nDo NOT skip this step.\nThen you should query the schema of the most
                    relevant tables.
                              """),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        llm = llm_factory.create_model(
            self.output_chat_model, model=state["chat_model"], tools=self.tools
        )
        chain: Runnable = prompt | llm
        return {"messages": [await chain.ainvoke(state, config=config)]}

    def create_default_state(self) -> GraphState:
        return {
            "name": self.name(),
            "messages": [],
            "chat_model": "",
        }

    @classmethod
    def name(cls) -> str:
        return "Data Science Chat"

    @property
    def output_chat_model(self) -> str:
        return "chat_model"

    @classmethod
    def chat_profile(cls) -> cl.ChatProfile:
        return cl.ChatProfile(
            name=cls.name(),
            markdown_description="VEGA AI",
            icon="/public/favicon.png",
            default=True,
        )

    @property
    def chat_settings(self) -> cl.ChatSettings:
        return cl.ChatSettings(
            [
                Select(
                    id="chat_model",
                    label="Chat Model",
                    values=sorted(
                        llm_factory.list_models(capabilities=self.capabilities)
                    ),
                    initial_index=0,
                ),
            ]
        )
