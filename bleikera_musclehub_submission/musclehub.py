
# coding: utf-8

# # Capstone Project 1: MuscleHub AB Test

# ## Step 1: Get started with SQL

# Like most businesses, Janet keeps her data in a SQL database.  Normally, you'd download the data from her database to a csv file, and then load it into a Jupyter Notebook using Pandas.
# 
# For this project, you'll have to access SQL in a slightly different way.  You'll be using a special Codecademy library that lets you type SQL queries directly into this Jupyter notebook.  You'll have pass each SQL query as an argument to a function called `sql_query`.  Each query will return a Pandas DataFrame.  Here's an example:

# In[54]:


# This import only needs to happen once, at the beginning of the notebook
from codecademySQL import sql_query


# In[55]:


# Here's an example of a query that just displays some data
sql_query('''
SELECT *
FROM visits
LIMIT 5
''')


# In[56]:


# Here's an example where we save the data to a DataFrame
df = sql_query('''
SELECT *
FROM applications
LIMIT 5
''')


# ## Step 2: Get your dataset

# Let's get started!
# 
# Janet of MuscleHub has a SQLite database, which contains several tables that will be helpful to you in this investigation:
# - `visits` contains information about potential gym customers who have visited MuscleHub
# - `fitness_tests` contains information about potential customers in "Group A", who were given a fitness test
# - `applications` contains information about any potential customers (both "Group A" and "Group B") who filled out an application.  Not everyone in `visits` will have filled out an application.
# - `purchases` contains information about customers who purchased a membership to MuscleHub.
# 
# Use the space below to examine each table.

# In[57]:


# Examine visits here
visits = sql_query('''
SELECT *
FROM visits
''')
print visits.head()
print visits.info()


# In[58]:


# Examine fitness_tests here
fitness_tests = sql_query('''
SELECT *
FROM fitness_tests
''')
print fitness_tests.head()
print fitness_tests.info()


# In[59]:


# Examine applications here
applications = sql_query('''
SELECT *
FROM applications
''')
print applications.head()
print applications.info()


# In[60]:


# Examine purchases here
purchases = sql_query('''
SELECT *
FROM purchases
''')
print purchases.head()
print purchases.info()


# We'd like to download a giant DataFrame containing all of this data.  You'll need to write a query that does the following things:
# 
# 1. Not all visits in  `visits` occurred during the A/B test.  You'll only want to pull data where `visit_date` is on or after `7-1-17`.
# 
# 2. You'll want to perform a series of `LEFT JOIN` commands to combine the four tables that we care about.  You'll need to perform the joins on `first_name`, `last_name`, and `email`.  Pull the following columns:
# 
# 
# - `visits.first_name`
# - `visits.last_name`
# - `visits.gender`
# - `visits.email`
# - `visits.visit_date`
# - `fitness_tests.fitness_test_date`
# - `applications.application_date`
# - `purchases.purchase_date`
# 
# Save the result of this query to a variable called `df`.
# 
# Hint: your result should have 5004 rows.  Does it?

# In[61]:


df = sql_query ('''
SELECT 
    visits.first_name,
    visits.last_name,
    visits.gender,
    visits.email,
    visits.visit_date,
    fitness_tests.fitness_test_date,
    applications.application_date,
    purchases.purchase_date

FROM visits
    LEFT JOIN fitness_tests 
        ON fitness_tests.first_name =  visits.first_name
        AND fitness_tests.last_name = visits.last_name
        AND fitness_tests.email = visits.email

    LEFT JOIN applications
        ON applications.first_name = visits.first_name
        AND applications.last_name = visits.last_name
        AND applications.email = visits.email

    LEFT JOIN purchases
        ON visits.first_name = purchases.first_name
        AND visits.last_name = purchases.last_name
        AND visits.email = purchases.email

WHERE visits.visit_date >= '7-1-17'
;
''')


# In[62]:


print df.head()
print df.info()


# ## Step 3: Investigate the A and B groups

# We have some data to work with! Import the following modules so that we can start doing analysis:
# - `import pandas as pd`
# - `from matplotlib import pyplot as plt`

# In[63]:


import pandas as pd
from matplotlib import pyplot as plt


# We're going to add some columns to `df` to help us with our analysis.
# 
# Start by adding a column called `ab_test_group`.  It should be `A` if `fitness_test_date` is not `None`, and `B` if `fitness_test_date` is `None`.

# In[64]:


df['ab_test_group'] = df.fitness_test_date.apply(lambda x: 'B' if pd.isnull(x) else 'A')
df.head()


# Let's do a quick sanity check that Janet split her visitors such that about half are in A and half are in B.
# 
# Start by using `groupby` to count how many users are in each `ab_test_group`.  Save the results to `ab_counts`.

# In[65]:


ab_counts = df.groupby('ab_test_group').email.count().reset_index().rename(columns = {'email': 'counts'})
ab_counts


# We'll want to include this information in our presentation.  Let's create a pie cart using `plt.pie`.  Make sure to include:
# - Use `plt.axis('equal')` so that your pie chart looks nice
# - Add a legend labeling `A` and `B`
# - Use `autopct` to label the percentage of each group
# - Save your figure as `ab_test_pie_chart.png`

# In[66]:


plt.pie(ab_counts.counts, autopct='%.2f')
plt.axis('equal')
plt.title('Groups for A-B Tests')
plt.legend(['with fitness test', 'without fitness test'])
plt.savefig('ab_test_pie_chart.png')
plt.show()


# ## Step 4: Who picks up an application?

# Recall that the sign-up process for MuscleHub has several steps:
# 1. Take a fitness test with a personal trainer (only Group A)
# 2. Fill out an application for the gym
# 3. Send in their payment for their first month's membership
# 
# Let's examine how many people make it to Step 2, filling out an application.
# 
# Start by creating a new column in `df` called `is_application` which is `Application` if `application_date` is not `None` and `No Application`, otherwise.

# In[67]:


df['is_application'] = df.application_date.apply(lambda x: 'No Application' if pd.isnull(x) else 'Application')
print df.info()
print df.head(2)


# Now, using `groupby`, count how many people from Group A and Group B either do or don't pick up an application.  You'll want to group by `ab_test_group` and `is_application`.  Save this new DataFrame as `app_counts`

# In[68]:


app_counts = df.groupby(['ab_test_group','is_application']).email.count().reset_index().rename(columns = {'email': 'counts'})


# In[69]:


print app_counts


# We're going to want to calculate the percent of people in each group who complete an application.  It's going to be much easier to do this if we pivot `app_counts` such that:
# - The `index` is `ab_test_group`
# - The `columns` are `is_application`
# Perform this pivot and save it to the variable `app_pivot`.  Remember to call `reset_index()` at the end of the pivot!

# In[70]:


app_pivot = app_counts.pivot(columns='is_application', index='ab_test_group', values='counts').reset_index()
print app_pivot


# Define a new column called `Total`, which is the sum of `Application` and `No Application`.

# In[71]:


app_pivot['Total'] = app_pivot.Application + app_pivot['No Application']
print app_pivot


# Calculate another column called `Percent with Application`, which is equal to `Application` divided by `Total`.

# In[72]:


app_pivot['Percent with Application'] = app_pivot.Application / app_pivot.Total
print app_pivot


# It looks like more people from Group B turned in an application.  Why might that be?
# 
# ** Interpretation: It could be that people who had to do a test were turned off by this and did not apply.**
# 
# We need to know if this difference is statistically significant.
# 
# Choose a hypothesis tests, import it from `scipy` and perform it.  Be sure to note the p-value.
# Is this result significant?

# In[73]:


from scipy.stats import chi2_contingency

# Creating the contingency-table
contingency = zip(app_pivot.Application, app_pivot['No Application'])


# In[74]:


print contingency


# In[75]:


_, pval, _, _ = chi2_contingency(contingency)

def interpretation(pval):
    if pval < 0.05: 
        return 'The difference is statistically significant. p-value: {}'.format(pval)
    else:
        return 'The difference is statistically not significant. p-value: {}'.format(pval)


# In[76]:


print interpretation(pval)


# ## Step 4: Who purchases a membership?

# Of those who picked up an application, how many purchased a membership?
# 
# Let's begin by adding a column to `df` called `is_member` which is `Member` if `purchase_date` is not `None`, and `Not Member` otherwise.

# In[77]:


df['is_member'] = df.purchase_date.apply(lambda x: 'Member' if pd.notnull(x) else 'Not Member')
print df.head()


# Now, let's create a DataFrame called `just_apps` the contains only people who picked up an application.

# In[78]:


just_apps = df[df.is_application == 'Application'].reset_index(drop=True)
print just_apps


# Great! Now, let's do a `groupby` to find out how many people in `just_apps` are and aren't members from each group.  Follow the same process that we did in Step 4, including pivoting the data.  You should end up with a DataFrame that looks like this:
# 
# |is_member|ab_test_group|Member|Not Member|Total|Percent Purchase|
# |-|-|-|-|-|-|
# |0|A|?|?|?|?|
# |1|B|?|?|?|?|
# 
# Save your final DataFrame as `member_pivot`.

# In[79]:


member_counts = just_apps.groupby(['ab_test_group', 'is_member']).email.count().reset_index().rename(columns = {'email': 'counts'})
member_pivot = member_counts.pivot(columns='is_member', index='ab_test_group', values='counts').reset_index()
member_pivot['Total'] = member_pivot.Member + member_pivot['Not Member']
member_pivot['Percent_Purchase'] = member_pivot.Member / member_pivot.Total
member_pivot


# It looks like people who took the fitness test were more likely to purchase a membership **if** they picked up an application.  Why might that be?
# 
# ** The people with the fitness test were less likely to pick up an application. Among those who did, they might have a slight bias to actually purchase. **
# 
# Just like before, we need to know if this difference is statistically significant.  Choose a hypothesis tests, import it from `scipy` and perform it.  Be sure to note the p-value.
# Is this result significant?

# In[80]:


contingency = zip(member_pivot.Member, member_pivot['Not Member'])
_, pval, _, _ = chi2_contingency(contingency)
print interpretation(pval)


# Previously, we looked at what percent of people **who picked up applications** purchased memberships.  What we really care about is what percentage of **all visitors** purchased memberships.  Return to `df` and do a `groupby` to find out how many people in `df` are and aren't members from each group.  Follow the same process that we did in Step 4, including pivoting the data.  You should end up with a DataFrame that looks like this:
# 
# |is_member|ab_test_group|Member|Not Member|Total|Percent Purchase|
# |-|-|-|-|-|-|
# |0|A|?|?|?|?|
# |1|B|?|?|?|?|
# 
# Save your final DataFrame as `final_member_pivot`.

# In[81]:


final_member = df.groupby(['ab_test_group', 'is_member']).email.count().reset_index().rename(columns={'email': 'counts'})


# In[82]:


final_member_pivot = final_member.pivot(columns='is_member', index='ab_test_group', values='counts').reset_index()
print final_member_pivot


# In[83]:


final_member_pivot['Total'] = final_member_pivot.Member + final_member_pivot['Not Member']
final_member_pivot['Percent_Purchase'] = final_member_pivot.Member / final_member_pivot.Total
final_member_pivot


# Previously, when we only considered people who had **already picked up an application**, we saw that there was no significant difference in membership between Group A and Group B.
# 
# Now, when we consider all people who **visit MuscleHub**, we see that there might be a significant different in memberships between Group A and Group B.  Perform a significance test and check.

# In[84]:


contingency = zip(final_member_pivot.Member, final_member_pivot['Not Member'])
_, pval, _, _ = chi2_contingency(contingency)
print interpretation(pval)


# ## Step 5: Summarize the acquisition funel with a chart

# We'd like to make a bar chart for Janet that shows the difference between Group A (people who were given the fitness test) and Group B (people who were not given the fitness test) at each state of the process:
# - Percent of visitors who apply
# - Percent of applicants who purchase a membership
# - Percent of visitors who purchase a membership
# 
# Create one plot for **each** of the three sets of percentages that you calculated in `app_pivot`, `member_pivot` and `final_member_pivot`.  Each plot should:
# - Label the two bars as `Fitness Test` and `No Fitness Test`
# - Make sure that the y-axis ticks are expressed as percents (i.e., `5%`)
# - Have a title

# First, we collect the data to be graphed:

# In[85]:


application_pct = (app_pivot['Percent with Application']).values
app_purchase_pct = member_pivot['Percent_Purchase'].values
total_visitors_purchase_pct = final_member_pivot['Percent_Purchase'].values

# The labels and ticks will be used for all three plots, therefore defined here.
x_labels = ['Fitness Test', 'No Fitness Test']


# ** Graph for Applications **

# In[86]:


plt.title('Applications Forms, by Group')
plt.bar(x_labels, application_pct)
ax = plt.subplot()
y_labels = ['0', '5%' , '10%', '15%', ]
y_values = [ 0, .05, .1, .15, .17 ]
ax.set_yticks(y_values)
ax.set_yticklabels(y_labels)
plt.savefig('application_pct_by_group.png')
plt.show()


# ** Graph for purchases among applications **

# In[87]:


plt.title('Purchases after Application')
plt.bar(x_labels, app_purchase_pct)
ax = plt.subplot()
y_labels = ['25%', '50%', '75%', '100%']
y_values = [.25, .5, .75, 1]
ax.set_yticks(y_values)
ax.set_yticklabels(y_labels)
plt.savefig('app_purchase_pct_by_group.png')
plt.show()


# ** Graph for overall customer conversion **

# In[88]:


plt.title('Overall Customer Conversion, by Group')
plt.bar(x_labels, total_visitors_purchase_pct)
ax = plt.subplot()
y_labels = ['0', '5%', '7%' , '8%', '9%', '10%','11%' ]
y_values = [ 0, .05, .07, .08, .09, .1,.11 ]
ax.set_yticks(y_values)
ax.set_yticklabels(y_labels)
plt.savefig('total_visitors_purchase_pct_by_group.png')
plt.show()

