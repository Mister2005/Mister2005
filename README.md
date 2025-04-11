<!-- BANNER (optional SVG or ASCII art) -->
![Banner](./assets/banner.svg)

# Hi there, I’m Varun Gupta 👋  
_Data Science enthusiast turning raw data into insights_  

<!-- PROFILE STATS -->
![GitHub stats](https://github-readme-stats.vercel.app/api?username=Mister2005&show_icons=true)  
![Top Languages](https://github-readme-stats.vercel.app/api/top-langs/?username=Mister2005&layout=compact)

<!-- INTRO -->
I’m a **Data Scientist** based in Mumbai who loves **data visualization**, **data analysis**, and **teaching**. Whether I’m building tools like [Automatic‑Data‑Visualizer‑AI‑Agent](https://github.com/Mister2005/Automatic-Data-Visualizer-AI-Agent) or crafting tutorials, I’m all about making data approachable and fun! 🚀

<!-- DYNAMIC QUOTE (auto‑updated daily via GitHub Action) -->
> <!--QUOTE-->“Data is the new oil.” — Clive Humby

<!-- FEATURED PROJECTS -->
## 🚀 Featured Project
- [Automatic‑Data‑Visualizer‑AI‑Agent](https://github.com/Mister2005/Automatic-Data-Visualizer-AI-Agent)  
  A Python‑based AI agent that automates the creation of interactive data visualizations.  

<!-- SKILLS -->
## 🛠️ Skills & Tools
- **Visualization:** Matplotlib, Seaborn, Plotly  
- **Analysis:** Pandas, NumPy, SciPy  
- **ML / AI:** scikit‑learn, TensorFlow, PyTorch  
- **Teaching:** Jupyter, Streamlit, Markdown  

<!-- CONTACT & SOCIAL -->
## 📫 Get in Touch
[![LinkedIn](https://img.shields.io/badge/LinkedIn-VarunGupta-blue)](https://www.linkedin.com/in/varun-gupta-220382290)  
[![Twitter Follow](https://img.shields.io/twitter/follow/yourhandle?style=social)](https://twitter.com/yourhandle)  

---

## ⚙️ How It Works

1. **Live Stats & Languages**  
   The two badges at the top auto‑refresh from [github-readme-stats](https://github.com/anuraghazra/github-readme-stats).  

2. **Daily Quote**  
   A GitHub Action runs every morning at 8 AM UTC to fetch a random programming quote and inject it between `<!--QUOTE-->` markers.  

   ```yaml
   # .github/workflows/update-quote.yml
   name: Update README Quote
   on:
     schedule:
       - cron: '0 8 * * *'
   jobs:
     update-quote:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - name: Fetch random quote
           id: quote
           run: |
             echo "::set-output name=text::$(curl -s https://programming-quotes-api.herokuapp.com/quotes/random | jq -r .en)"
         - name: Update README
           run: |
             sed -i "s|<!--QUOTE-->.*|<!--QUOTE-->\"${{ steps.quote.outputs.text }}\"|" README.md
         - uses: EndBug/add-and-commit@v9
           with:
             author_name: github-actions[bot]
             author_email: github-actions[bot]@users.noreply.github.com
             message: "chore: update daily quote"
```
