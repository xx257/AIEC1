

## # Session 10: LLM Servers


| 📰 Session Sheet                                                                                                                            | ⏺️ Recording                                                                                                                                           | 🖼️ Slides                                              | 👨‍💻 Repo    | 📝 Homework                                                  | 📁 Feedback                                         |
| ------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------- | ------------- | ------------------------------------------------------------ | --------------------------------------------------- |
| [Session 10: LLM Servers](https://github.com/AI-Maker-Space/The-AI-Engineering-Certification-v1.0/tree/main/00_Docs/Modules/10_LLM_Servers) | [Recording!](https://us02web.zoom.us/rec/share/zXd6__uO2RwCmJUmNyGKY01sbwYjjrkpDDNPbfK_Es0MANaqRpFOqqYX4sEVYY1d.gJwTZk1729siXnjj) passcode: `^1$@$R@.` | [Session 10 Slides](https://canva.link/953giejzt5igxvw) | You are here! | [Session 10 Assignment](https://forms.gle/hKxFnEM8U16fCCnG8) | [Feedback 7/2](https://forms.gle/uj2QvYjHfHKFFQ8a6) |


**⚠️!!! PLEASE BE SURE TO SHUTDOWN YOUR DEDICATED ENDPOINT ON FIREWORKS AI WHEN YOU'RE FINISHED YOUR ASSIGNMENT !!!⚠️**

# Build 🏗️

In today's assignment, we'll be creating Fireworks AI endpoints, and then building a RAG application.

- 🤝 Breakout Room #1
  - Set-up Open Source Endpoint (Instructions [here](./ENDPOINT_SETUP.md)) ((This process may take 15-20min.))
  - Test Endpoint and Embeddings with the `endpoint_slammer.ipynb` notebook.
- 🤝 Breakout Room #2
  - Use the Open Source Endpoints to build a RAG LangGraph application

# Ship 🚢

The completed notebook and your RAG app/notebook!

### Deliverables

- A short Loom of either:
  - the notebook and the RAG application you built for the Main Homework Assignment; or
  - the notebook you created for the Advanced Build

# Share 🚀

Make a social media post about your final application!

### Deliverables

- Make a post on any social media platform about what you built!

Here's a template to get you started:

```
🚀 Exciting News! 🚀

I am thrilled to announce that I have just built and shipped a RAG application powered by open-source endpoints! 🎉🤖

🔍 Three Key Takeaways:
1️⃣
2️⃣
3️⃣

Let's continue pushing the boundaries of what's possible in the world of AI and question-answering. Here's to many more innovations! 🚀
Shout out to @AIMakerspace !

#LangChain #QuestionAnswering #RetrievalAugmented #Innovation #AI #TechMilestone

Feel free to reach out if you're curious or would like to collaborate on similar projects! 🤝🔥
```

# Submitting You Homework

## Main Homework Assignment

Follow these steps to prepare and submit your homework assignment:

1. Follow the instructions in `ENDPOINT_SETUP.md`
2. Replace both `model` values in `endpoint_slammer.ipynb` with the `gpt-oss` endpoint you created in Step 1
3. Run the code cells in `endpoint_slammer.ipynb`
4. Respond to the questions in the section below
5. Build a sample RAG
6. Record a Loom video reviewing what you have learned from this session

**⚠️!!! PLEASE BE SURE TO SHUTDOWN YOUR DEDICATED ENDPOINT ON FIREWORKS AI WHEN YOU HAVE FINISHED YOUR ASSIGNMENT !!!⚠️**

## Questions

### ❓ Question #1:

What is the difference between serverless and dedicated endpoints?

#### ✅ Answer:

Serverless endpoints run on the provider’s shared GPU infrastructure. They require almost no operations and are billed based on usage, such as tokens, so they are a good choice for quick experiments or workloads with unpredictable traffic. The tradeoff is that resources are shared with other users, which can lead to rate limits or less predictable latency.

Dedicated endpoints provide your own GPU resources. They are billed by GPU runtime, so they can keep costing money even when the app is idle. In exchange, they provide more predictable performance and control over settings like GPU type, replica count, quantization, autoscaling, and scale-to-zero.

Pick serverless when I want simple setup, low maintenance, and pay-per-use. Pick dedicated when I need consistent performance, customization, and guaranteed capacity.

### ❓ Question #2:

Why is it important to consider token throughput and latency when choosing an LLM for user-facing applications?

#### ✅ Answer:

Token throughput and latency matter for user-facing applications because they directly affect user experience and scalability. Time to first token controls how quickly the app feels responsive, while token throughput controls how fast the response finishes streaming.

For user-facing apps, token throughput and latency matter because they determine whether the product feels responsive, reliable, and affordable to run. For exmaple, a chat app is not only judged by answer quality because users also care about how quickly it starts responding and whether the stream continues smoothly.

These metrics also show how much traffic an endpoint can handle before requests start queueing, which affects tail latency and the user experience under load. A model that is very accurate but slow or expensive may be better for deep tasks, while a faster and cheaper model may be better for everyday interactions. So choosing an LLM is really a tradeoff between quality, speed, capacity, and cost.

## Activity 1: RAGAS Evaluation with Cost Analysis

Use RAGAS to evaluate your open-source Fireworks AI powered RAG app against an OpenAI `gpt-4.1-mini` powered equivalent. Compare retrieval quality, answer faithfulness, and end-to-end accuracy across both providers.

Additionally, instrument both pipelines with **LangSmith** to capture token usage and cost per query. Use LangSmith's tracing and cost dashboards to compare the total cost of running each provider at scale. Include your evaluation results, cost breakdown, and analysis in your Loom video.

## Advanced Activity: Local Models

Swap out the Fireworks AI endpoints for **locally-running open-source models** using [Ollama](https://ollama.com/) or another local inference server of your choice. Run both your embedding model and your chat model locally, and rebuild the RAG pipeline on top of them.

- Compare quality and latency between the local setup and your Fireworks AI hosted endpoint.
- Reflect: what are the trade-offs of local models vs. managed endpoints in a production setting?

Include your findings and a demo in your Loom video.