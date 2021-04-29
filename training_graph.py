# %%
import matplotlib.pyplot as plt 
import seaborn as sns 

scores = []
f = open("bestOf.csv", "r")
for line in f:
  if line.strip() != "":
    scores.append(int(line.strip().split("_")[1]))
f.close()
x = [i for i in range(len(scores))]
# %%
sns.lineplot(x=x,y=scores)
plt.xlabel("Generation Number")
plt.ylabel("Amount of Sun Hitting Panels (pixels)")
plt.title("Training Over Generations")
plt.show()
# plt.savefig("Training.png")




# %%
