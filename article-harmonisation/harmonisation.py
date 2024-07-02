import json
import os
from langchain.tools.render import format_tool_to_openai_function
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import END, StateGraph
from langgraph.prebuilt.tool_executor import ToolExecutor, ToolInvocation
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tracers.context import tracing_v2_enabled
from langsmith import Client
from dotenv import load_dotenv
from models import Llama
from langchain_huggingface import HuggingFaceEndpoint
from typing import TypedDict, Optional
from langgraph.graph import StateGraph
from prompt import LLMPrompts

article = """
        Breast cancer is the number one cancer among women in Singapore. You can protect yourself by taking active preventive measures to protect yourself against them. Besides being well informed about these conditions, you can protect yourself by going for regular health screenings.

        Breast Cancer Screening
        Beyond the recommended monthly breast self-examinations, the best way to protect yourself from breast cancer is to go for regular mammograms. A mammogram can detect tiny lumps that cannot be felt by the hand. Early detection, followed by treatment and good control of the condition can result in better chances of surviving this cancer, lowering the risk of serious complications.
        Women who are 50 years old and above are recommended to go for a mammogram once every two years. Women 40 to 49, can screen for breast cancer, annually, provided their doctor has discussed the benefits and limitations with them. It is important to make an informed choice about going for screening.
        Related: Cancer Facts You Cannot Ignore

        Subsidy for Mammograms
        Under the Health Promotion Boards (HPB) Screen for Life (SFL)[1], women aged 50 years and above can benefit from subsidised mammogram screenings which cost $50 for Singapore citizens, $75 for Permanent Residents (PRs), $37.50 for Merdeka Generation Cardholders and $25 for Pioneer Generation Cardholders at participating locations.
        Eligibility for subsidised mammograms under HPBs Screen for Life is as follows:
        [1]Screen for Life refers to HPBs screening programmes for cardiovascular diseases and selected cancers. For more information, please visit Screen for Life..

        Tips on Breast Cancer Screening Subsidies
        If you are 50 years old and above, you can use your Medisave or the Medisave account of an immediate family member for your mammogram at Medisave-approved centres, including participating centres under HPBs Screen for Life that are listed in this article. The full list of approved centres can be found on the Ministry of Health's (MOH) website.
        You can use up to $500 per Medisave account a year under the Medisave500 scheme.
        The Singapore Cancer Society offers free mammography services at $0 for women aged 50 years and above, who have not gone for this screening in the last two years and have a valid Blue or Orange Community Health Assist Scheme Card (CHAS) card, at their Multi-Service Centre in Bishan.
        Related: Breast Cancer Screening Now Free for Eligible Singaporeans

        Where to Go for Screenings
        The following centres offer subsidised mammogram screening. You are encouraged to call ahead to make an appointment.

        Singapore Cancer Society Clinic @ Bishan
        For women with a valid Blue or Orange Community Health Assist Scheme (CHAS) card Tel: 1800 727 3333^

        Polyclinics
        Call 6275 6443 to make an appointment.
        Alternatively, you may use their online form or through HealthHub.
        Call 6370 6556 to make an appointment.
        Alternatively, you may use their online form or email nuhsd_contact@nuhs.edu.sg
        Call 6536 6000 to make an appointment.
        Alternatively, you may use their online form.

        Useful Links
        1. Understanding Breast Cancer Learn more about breast cancer, its risk factors, treatment options and mammogram procedures.
        2. Breast Cancer Foundation / Singapore Cancer Society All matters relating to breast cancer, from mammogram procedures to public education programmes.
        Learn more about breast cancer, its risk factors, treatment options and mammogram procedures.
        All matters relating to breast cancer, from mammogram procedures to public education programmes.

        Contact Information

        Screen for Life
        Telephone: 1800 223 1313^ Email: HPB_Mailbox@hpb.gov.sg
        """

load_dotenv()

os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "")
os.environ["HUGGINGFACEHUB_API_TOKEN"]= os.getenv("HUGGINGFACEHUB_API_TOKEN", "")

MODEL = "meta-llama/Meta-Llama-3-8B-Instruct"
MAX_NEW_TOKENS = 3000
NODE_ROLES = ['Researcher', "Compiler"]


prompter = LLMPrompts()

class GraphState(TypedDict):
    article: Optional[str] = None
    keypoints: Optional[str] = None
    response: Optional[str] = None
    

workflow = StateGraph(GraphState)

def researcher_node(state):
    llm = HuggingFaceEndpoint(endpoint_url=MODEL, max_new_tokens=MAX_NEW_TOKENS)
    comparer_agent = Llama(llm, prompter.return_researcher_prompt(), NODE_ROLES[0])
    article = state.get('article', '').strip()
    keypoints = comparer_agent.generate_text(article)
    return {"keypoints": keypoints}

# def handle_greeting_node(state):
#     return {"response": "Hello! How can I help you today?"}

# def handle_search_node(state):
#     question = state.get('question', '').strip()
#     search_result = f"Search result for '{question}'"
#     return {"response": search_result}


workflow.add_node("get_keypoints", researcher_node)
# workflow.add_node("handle_greeting", handle_greeting_node)
# workflow.add_node("handle_search", handle_search_node)

# def decide_next_node(state):
#     return "handle_greeting" if state.get('classification') == "greeting" else "handle_search"

# workflow.add_conditional_edges(
#     "classify_input",
#     decide_next_node,
#     {
#         "handle_greeting": "handle_greeting",
#         "handle_search": "handle_search"
#     }
# )

workflow.set_entry_point("get_keypoints")

workflow.add_edge('get_keypoints', END)

app = workflow.compile()

inputs = {"article": article}
result = app.invoke(inputs)
print(result['keypoints'])

