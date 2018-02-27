def parse_file(filename, parse_function):
    f = open('inputs/'+filename, 'r')
    content = f.readlines()
    f.close()
    return parse_function(content)