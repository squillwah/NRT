
# to do

Stuff to be done

- **References/Dataset**
    - [ ] Acquire Reference Data pre 2022                                   
        - For verified set / base references.
    - [ ] More diverse dataset generation / policies. 
    - [ ] Verify accuracy of format style compilers, component codes.       
        - Needed to mark absent components in evaluation matrices.
    - [ ] Calculate format-wise holistic scores, include in dsentries with component codes.
        - For proper absent components in the model performance evaluation (CSV).
    - [ ] Define weights for reference components                           
        - Which matter more when calculating mutation severity? Also needs to not be overly biased by component count. 
        - How to reconsile holistic binary true/false (all comps ANDed) with a lower severity score? Should the ANDing be weighted somehow, and become a True? Probably not. It should be false for any mutation.

- **Models/Responses**
    - [ ] Rewrite prompts in schema with 'valid'/'invalid' framing.         
        - Instead of the vague 'generated' framing.
    - [ ] Catch and retry malformed request errors in orouterapi.py         
        - A 'chunkedencodingerror' killed the last test.
    - [ ] Add threading / concurrent requests to multimodel\_evaluator
    - [ ] Reimplenting internet search capabilities.
        - So we can run **experiments** with and without.

- **Assessing Model Responses**
    - [ ] Averaging performance and confidence matrices for all models against all components.
    - [ ] Another csv with model answer | true answer? 
        - Instead of or as an intermediary step before comparing both for performance. Redundant.

- **other**
    - [ ] More models? (for a greater variation of intellgience)
    - [ ] Properly defining "real" / "valid" vs "fake" / "invalid" in our context. For **paper**.
    - Outlines of paper/presentation sections
        - Stating the phenomona (fabricated references in biomedical literature) briefly explain possible causes (hallucination, llm use), effects.
        - Introduce our focus, the question(s) we're asking.
            - What new knowledge are we adding to field?
            - If the models are generating so many of fake cites, how are they at detecting them? Would the be good at detecting them? If so, then why do they generate them in the first place; what is the cause of that disparity?
            - How much should waffle about the road to our focus, from our vague ideas at the start? Probs not much or at all.
        - Our methods, how we went about exploring our questions
            - Generating datasets of fake references, running against many models, grading results, ...
            - Tools we used...
            - Again, how much context should we give to the development/maturation of our methods? The things we tried but didn't work, other paths we considered? Is any of that worth mentioning?
        - Data findings ...
        - Our thoughts/conclusions on the findings ...
            - What new stuff did we find / not find?
            - What more could be done on top of our work?
            


<br>

---

# Random stuff / tangential

- What kinds of corpus are our models trained on? This affects their performance. To mention in the **paper**.
- When a model is showing a high error for a component, we should look at its reasoning and confidences. A low confidence with sound reasoning is still a working system.
- Could we **experiment** using another LLM to extract trends/patterns from reasoning text?
- Problem of being too exact in prompts. The power of the prompt. Impact of the prompt.
  - In the prompt sections regarding specific components, we still want the model to consider the context of the entire reference. A year or page number in isolation are always 'real'.
  - So far they are. Maybe really stupid models wont. What stupid models can we test?
  - Could **experiment** with different prompts on the same set, compare for significant differences.
  - Prompts should focus on the existence of a component (instead of a vague framing like 'generated'), but not too specific as to bias the model one way or pigeon hole their analysis as stated.
  - The problem of prompts effect on model responses is a big one, we can talk about our dealings with it and suggest ideas for "further work" in the **paper**
- Some models (with newer cutoffs) would have advantage with papers after 2022. It would not be a 'fair test'. Should we **experiment** with a smaller new paper (published recently) set? We already have 100.
  - A paper it hasn't been trained on isn't far off from a 'hallucinated' paper in its worldview. Plus since we built the fake references off them, it has nothing to check those against either. Bad.
- Possible weights:
  - journal important, title even more, page not so much, pmcid pretty not so much, date a little more, authors quite important, etc......

## Analysis

- Accuracy x Severity scatterplots
  - Per model, references are points.           *(could also do all models)*
  - Have plots by component, plus holistic.
  - Expecting accuracy line go down with severity.
- Averaging 
  - Performances for models, across all references.
  - Confidence scores, which components are models most confident in evaluating on average?
- Some kind of multiplication of avg perf * avg conf?
- F1 / precision / recall / auc

### Conceptual

- Which models are 'better' and why?
- Attempting to answer why we get the results we do.

---









<br><br><br><br><br><br><br>

```
░░░░░░▄▄▄░░▄██▄░░░    ░░░░░░▄▄▄░░▄██▄░░░     ░░░░░░▄▄▄░░▄██▄░░░    ░░░░░░▄▄▄░░▄██▄░░░   
░░░░░▐▀█▀▌░░░░▀█▄░░░  ░░░░░▐▀█▀▌░░░░▀█▄░░░   ░░░░░▐▀█▀▌░░░░▀█▄░░░  ░░░░░▐▀█▀▌░░░░▀█▄░░░ 
░░░░░▐█▄█▌░░░░░░▀█▄░░ ░░░░░▐█▄█▌░░░░░░▀█▄░░  ░░░░░▐█▄█▌░░░░░░▀█▄░░ ░░░░░▐█▄█▌░░░░░░▀█▄░░
░░░░░░▀▄▀░░░▄▄▄▄▄▀▀░░ ░░░░░░▀▄▀░░░▄▄▄▄▄▀▀░░  ░░░░░░▀▄▀░░░▄▄▄▄▄▀▀░░ ░░░░░░▀▄▀░░░▄▄▄▄▄▀▀░░
░░░░▄▄▄██▀▀▀▀░░░░░░░  ░░░░▄▄▄██▀▀▀▀░░░░░░░   ░░░░▄▄▄██▀▀▀▀░░░░░░░  ░░░░▄▄▄██▀▀▀▀░░░░░░░ 
░░░█▀▄▄▄█░▀▀░░        ░░░█▀▄▄▄█░▀▀░░         ░░░█▀▄▄▄█░▀▀░░        ░░░█▀▄▄▄█░▀▀░░       
░░░▌░▄▄▄▐▌▀▀▀░░       ░░░▌░▄▄▄▐▌▀▀▀░░        ░░░▌░▄▄▄▐▌▀▀▀░░       ░░░▌░▄▄▄▐▌▀▀▀░░      
▄░▐░░░▄▄░█░▀▀ ░░      ▄░▐░░░▄▄░█░▀▀ ░░       ▄░▐░░░▄▄░█░▀▀ ░░      ▄░▐░░░▄▄░█░▀▀ ░░     
▀█▌░░░▄░▀█▀░▀ ░░      ▀█▌░░░▄░▀█▀░▀ ░░       ▀█▌░░░▄░▀█▀░▀ ░░      ▀█▌░░░▄░▀█▀░▀ ░░     
░░░░░░░▄▄▐▌▄▄░░░      ░░░░░░░▄▄▐▌▄▄░░░       ░░░░░░░▄▄▐▌▄▄░░░      ░░░░░░░▄▄▐▌▄▄░░░     
░░░░░░░▀███▀█░▄░░     ░░░░░░░▀███▀█░▄░░      ░░░░░░░▀███▀█░▄░░     ░░░░░░░▀███▀█░▄░░    
░░░░░░▐▌▀▄▀▄▀▐▄░░     ░░░░░░▐▌▀▄▀▄▀▐▄░░      ░░░░░░▐▌▀▄▀▄▀▐▄░░     ░░░░░░▐▌▀▄▀▄▀▐▄░░    
░░░░░░▐▀░░░░░░▐▌░░    ░░░░░░▐▀░░░░░░▐▌░░     ░░░░░░▐▀░░░░░░▐▌░░    ░░░░░░▐▀░░░░░░▐▌░░   
░░░░░░█░░░░░░░░█░░░   ░░░░░░█░░░░░░░░█░░░    ░░░░░░█░░░░░░░░█░░░   ░░░░░░█░░░░░░░░█░░░  
```
