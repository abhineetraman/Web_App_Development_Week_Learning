import sys
from jinja2 import Template
import pyhtml as h
import matplotlib.pyplot as plt

# print(sys.argv)

template_1 = '''
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
    <style>
        table {
            border: 1px solid black;
            border-collapse: none;
            text-align: none;
        }

        th,
        td {
            border: 1px solid black;
        }

        #last_row {
            text-align: center;
        }
    </style>
</head>

<body>
    <h1>Student Details</h1>
    <table>
        <thead>
            <tr>
                <th>Student id</th>
                <th>Course id</th>
                <th>Marks</th>
            </tr>
        </thead>

        {% for dict in list_of_dict %}
        <tr>
            <td>{{ dict["student_id"] }}</td>
            <td>{{ dict["course_id"] }}</td>
            <td>{{ dict["marks"] }}</td>
        </tr>
        {% endfor %}

        <tr>
            <td id="last_row" colspan="2">Total Marks</td>
            <td>{{ sum }}</td>
        </tr>

    </table>
</body>

</html>
'''

template_2 = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
    <style>
        table {
            border: 1px solid black;
            border-collapse: none;
            text-align: none;
        }

        th,
        td {
            border: 1px solid black;
        }
    </style>    
</head>
<body>

<h1>Course Details</h1>

    <table>
        <thead>
            <tr>
                <th>Average Marks</th>
                <th>Maximum Marks</th>
            </tr>
        </thead>

        <tr>
            <td>{{ avg }}</td>
            <td>{{ max }}</td>
        </tr>
    </table>    
    <img src = "hist.png">
</body>
</html>
'''


def generate_error():

    t = h.html(
        h.head(
            h.title('Error Page')
        ),
        h.body(
            h.h1('Wrong Inputs'),
            h.div(h.p('Something went wrong'))
        )
    )
    output = t.render()
    return output


def generate_template_1(student_id):
    ''''''
    sum = 0
    list_of_dict = []
    for row in info:
        if(student_id == row[0]):
            list_of_dict.append(
                {"student_id": student_id, "course_id": row[1], "marks": row[2]})
            sum += row[2]

    template_obj = Template(template_1)
    output = template_obj.render(list_of_dict=list_of_dict, sum=sum)

    return output


def generate_template_2(course_id):
    ''''''
    sum = 0
    max = -1
    marks = []
    for row in info:
        if(course_id == row[1]):

            marks.append(row[2])
            sum += row[2]
            if(max < row[2]):
                max = row[2]

    avg = sum/len(marks)
    #marks_numpy = np.array(marks)
    plt.hist(marks)
    plt.xlabel("Marks")
    plt.ylabel("Frequency")
    # plt.show()
    plt.savefig("hist.png")

    template_obj = Template(template_2)
    output = template_obj.render(avg=avg, max=max)
    return output


data_file = open('data.csv', 'r')
data_file_content = data_file.readlines()[1:]
# print(data_file_content)

st_ids = set()
c_ids = set()
info = []

for line in data_file_content:
    details = line.strip().split(',')
    # print(details)
    st_ids.add(details[0].strip())
    c_ids.add(details[1].strip())
    info.append([details[0].strip(), details[1].strip(),
                int(details[2].strip())])
# print(info)
# print(st_ids,c_ids)

if(len(sys.argv) < 3):
    output = generate_error()
else:
    if(sys.argv[1] == '-s'):

        if(sys.argv[2] in st_ids):
            output = generate_template_1(student_id=sys.argv[2])

        else:
            output = generate_error()

    elif(sys.argv[1] == '-c'):

        if(sys.argv[2] in c_ids):
            output = generate_template_2(course_id=sys.argv[2])

        else:
            output = generate_error()

    else:
        output = generate_error()


f = open('output.html', 'w')
f.write(output)
f.close()
