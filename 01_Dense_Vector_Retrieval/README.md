# Session 1: Dense Vector Retrieval

### [Quicklinks]()


| 📰 Module Sheet                                                                  | ⏺️ Recording                                                                                                                                           | 🖼️ Slides                                             | 👨‍💻 Repo    | 📝 Homework                                                 | 📁 Feedback                                         |
| -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------ | ------------- | ----------------------------------------------------------- | --------------------------------------------------- |
| [Dense Vector Retrieval](../00_Docs/Modules/01_Dense_Vector_Retrieval/README.md) | [Recording!](https://us02web.zoom.us/rec/share/sHWvo0Nd1aI0SEhKecOLEX9kFGVJJAdYfsKiuTmm8t85W48Z2lnjpnzTy8jAd8R5.PwuqibGwAZhvDd8c) passcode: `C62n^@Q!` | [Session 1 Slides](https://canva.link/htfqf8i39yejyhn) | You are here! | [Session 1 Assignment](https://forms.gle/Z9qskfVaAvPjn6gz8) | [Feedback 6/2](https://forms.gle/21a2uoL9DVZPwgJP6) |


## 🏗️ How AIM Does Assignments

> 📅 **Assignments will always be released to students as live class begins.** We will never release assignments early.

Each assignment will have a few of the following categories of exercises:

- ❓ **Questions** - these will be questions that you will be expected to gather the answer to. These can appear as general questions, or questions meant to spark a discussion in your breakout rooms.
- 🏗️ **Activities** - these will be work or coding activities meant to reinforce specific concepts or theory components.
- 🚧 **Advanced Builds (optional)** - Take on a challenge. These builds require you to create something with minimal guidance outside of the documentation.

## Main Assignment

In this assignment, you will build a vector RAG application using LangChain v1, OpenAI embeddings, and Qdrant.

The main notebook is:

```text
01_Cat_Health_Vector_RAG_LangChain_Qdrant.ipynb
```

The notebook uses the bundled cat health guideline PDF in `data/cat_health_guidelines.pdf`.

### Setup

From this folder, install the environment with uv:

```bash
uv sync
```

Then open the notebook in Cursor or VS Code and select the Python/Jupyter environment created by uv.

You will also need an OpenAI API key available when running the notebook.

---

## 🏗️ Activity #1: Embedding Similarity

Run the embedding similarity primer in the notebook.

You will compare embeddings for terms like:

- `king`
- `queen`
- `banana`
- `cat`
- `veterinarian`
- `cat health guidelines`

#### ❓Question #1

Why is cosine similarity useful for dense vector retrieval?

##### ✅ Answer: Cosine similarity measures the angle in between vectors other than its magnitude in the embedding space and for embeddings, the **meaning is often encoded more in the direction than in the length**, so cosine similarity better reflects semantic similarity in between terms.

---

## 🏗️ Activity #2: Build the Vector RAG Pipeline

Run the notebook sections that:

1. Load the PDF into LangChain `Document` objects
2. Split the document into chunks
3. Embed the chunks
4. Store the chunk embeddings in in-memory Qdrant
5. Retrieve relevant chunks with similarity scores
6. Generate an answer grounded in retrieved context

#### ❓Question #2

Why is metadata important for a RAG application?

##### ✅ Answer: Metadata can provide more structured information about documents that embeddings alone cannot capture. Other than just comparing the sematic similarity in between user query and document chunks, metadata can be used to improve precision and ensure the model retrieves relevant, authorized, and up-to-date information.

#### ❓Question #3

What tradeoff do we make when choosing chunk size and chunk overlap?

##### ✅ Answer:  Smaller chunk helps with improving retrieval accuracy but can lose important context while larger chuck is the opposite with providing more but maybe unnessary context and higher token cost. Overlap helps prevent important information from being split across chunk boundaries and improving recalls, but increases storage, embedding costs, and duplicate retrievals.

#### ❓Question #4

What does a similarity score help you understand, and what does it not prove by itself?

##### ✅ Answer: A similarity score for ranking the retrieval results and also tells us how semantically similar a query embedding is to a document embedding. It does not prove that the retrieved document has the correct answer, is factually accurate, is the best available result, and fully matches the user’s intents.

---

## 🏗️ Activity #3: Vibe Check Retrieval Quality

Run the notebook's vibe check queries and inspect both:

- The retrieved context
- The generated answer

#### ❓Question #5

For the vibe check queries, did the retrieved context seem relevant before generation? Why or why not?

##### ✅ Answer: The retrieved context seems pretty relevant for the first three questions which are all cat health related. But for the last one, it's not relevant at all. Just like what we answered in the first question, we retrieve and rank the context based on the cosine similarity in between their vector embbedings. When input query and document is already semantic similar (all about cat health), the more confidence we can get from the the resources and vice versa.

---

## 🏗️ Activity #4: Tune Retrieval

Improve retrieval quality by changing one or more of:

- Chunk size
- Chunk overlap
- Retrieval `k`
- Query wording

Document what changed and whether retrieval improved.

##### Settings Changed: I tried to decrease the chunk size and chunk overlap to be much smaller (1000 -> 200), (200 -> 40) and I noticed that if i do that, the accurate drops significantly, because the context becomes much shorter. the results are just not related to what i ask.

- 

##### Results: Significantly reduced accuracy and more processing time.

---

## Optional Deep Dive: RAG From Scratch

If you want to look underneath the library abstractions, run the optional reference notebook:

```text
02_Cat_Health_Vector_RAG_From_Scratch.ipynb
```

It builds the same retrieval pipeline again with only:

- `pypdf` for extracting text from the PDF
- Python standard-library HTTP requests for calling OpenAI
- Handcrafted document, chunking, embedding, similarity-search, vector-store, and generation primitives

This notebook is a reference walkthrough, not an additional assignment. Its purpose is to make the responsibilities hidden by LangChain, Qdrant, and provider SDKs visible.

---

## Submitting Your Homework

### Main Assignment

Follow these steps to prepare and submit your homework:

1. Pull the latest updates from upstream into the main branch of your AIE9 repo:

```bash
git checkout main
git pull upstream main
git push origin main
```

1. Start Cursor from the `01_Dense_Vector_Retrieval` folder.
2. Complete the notebook.
3. Answer the questions in this `README.md`.
4. Add, commit, and push your modified work to your origin repository.

When submitting your homework, provide the GitHub URL to your AIE9 repo.