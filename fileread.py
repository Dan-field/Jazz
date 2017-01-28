# First try at reading chord symbols from a text file

# open the file and read the lines into the list called "content"
# note each line of the text file becomes a separate list element
fname = "Autumn.txt"
with open(fname) as f:
   content = f.readlines()
   
# Remove the 'newline' characters from the elements
content = [x.strip('\n') for x in content]
   
print(content)