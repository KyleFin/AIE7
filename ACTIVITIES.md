##### 🏗️ Activity #1:

Please evaluate your system on the following questions:

1. Explain the concept of object-oriented programming in simple terms to a complete beginner. 
    - Aspect Tested:
      - e2e flow from UI to backend (API keys etc)
      - Model's ability to give a reasonable explanation in an area I'm familiar with.
      - Formatting within the app (text in `**` should be rendered as bold)
    - My app successfully returned a reasonable response. The markdown formatting (bold) can be improved.
      ![image](https://github.com/user-attachments/assets/5069e117-978a-41f0-96e5-e4e4fe8f9c33)

2. Read the following paragraph and provide a concise summary of the key points… (I pasted the abstract of the paper about [LLM use degrading our brain performance](https://arxiv.org/abs/2506.08872))
    - Aspect Tested:
      - Model's ability to understand a block of text, recognize key points, and provide a simpler summary that maintains the original meaning.
    - My app provided a reasonable (and useful) summary that was easier for me to understand than the original.
      ![image](https://github.com/user-attachments/assets/129a06d0-893b-47fd-a5b3-eb0bf152ffdc)

3. Write a short, imaginative story (100–150 words) about a robot finding friendship in an unexpected place.
    - Aspect Tested:
      - Model's ability to expand on a small instruction to create something larger (with a specific length and topic).
    - My app provided a story that fits the description with 114 words.
      ![image](https://github.com/user-attachments/assets/62300b5e-1521-4d7e-89b8-3b46a69e5c01)

4. If a store sells apples in packs of 4 and oranges in packs of 3, how many packs of each do I need to buy to get exactly 12 apples and 9 oranges?
    - Aspect Tested:
      - Ability to understand mathematical intent, discern between which details are important, and work through multiple steps to calculate a precise expected answer.
    - My app succesfully understood and solved the problem, explaining its work clearly.
    ![image](https://github.com/user-attachments/assets/c9ed4a9c-5c6c-4163-90a9-383569c18c1f)

      
5. Rewrite the following paragraph in a professional, formal tone… (I pasted the lyrics of Prince of Bel-Air theme :)
    - Aspect Tested:
      - Ability to understand the meaning of a passage and restate it in a different style.
    - Pretty impressive! lol
    ![image](https://github.com/user-attachments/assets/24b67cc2-c4b0-452a-aacf-1a9dd187e26c)

##### 🚧 Advanced Build:

Please make adjustments to your application that you believe will improve the vibe check done above, then deploy the changes to your Vercel domain [(see these instructions from your Challenge project)](https://github.com/AI-Maker-Space/The-AI-Engineer-Challenge/blob/main/README.md) and redo the above vibe check.

> NOTE: You may reach for improving the model, changing the prompt, or any other method.

ANSWER: I used vibe coding to add better markdown handling for bold and bulleted lists. The vibes of the model responses seem good to me, so I left the model and prompt as they were.

Vercel URL: https://ai-bootcamp-challenge.vercel.app/

![image](https://github.com/user-attachments/assets/39f443ab-385c-4a2f-ba05-340e02a7d791)

(Compare to #4 above)
![image](https://github.com/user-attachments/assets/5d259f34-f57e-410b-ac42-ad0df05c924f)

##### 🧑‍🤝‍🧑❓ Discussion Question #1:

What are some limitations of vibe checking as an evaluation tool?

- We are only checking a tiny subset of the possible inputs our app could encounter.
- We're not testing its knowledge about domains in which we're not experts.
- We didn't test the consistency of the model.
- We didn't check if it can be made to generate offensive or inappropriate content (accidentally or maliciously)
