import jinja2
import os
import argparse

parser=argparse.ArgumentParser()
parser.add_argument("filename")
#parser can have any arguments, whatever you want!

parsed, unknown = parser.parse_known_args() #this is an 'internal' method
# which returns 'parsed', the same as what parse_args() would return
# and 'unknown', the remainder of that
# the difference to parse_args() is that it does not exit when it finds redundant arguments

for arg in unknown:
    if arg.startswith(("-", "--")):
        #you can pass any arguments to add_argument
        parser.add_argument(arg, type=str)

args=parser.parse_args()
print args



with open(args.filename) as f:
  templatestr = f.read()

t = jinja2.Template(templatestr)
rendered_template = t.render(env=os.environ, **vars(args))
print rendered_template

