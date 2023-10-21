from flask import render_template, Flask, request
import matplotlib.pyplot as plt

st_ids = ['1004', '1001', '1009', '1003', '1007', '1008', '1060', '1090', '1080', '1005', '1030', '1002', '1000']
c_ids = ['2004', '2001', '2002', '2003']
info = [['1001', '2001', 56], ['1002', '2001', 67], ['1003', '2001', 78], ['1004', '2001', 90], ['1005', '2001', 45], ['1001', '2002', 58], ['1002', '2002', 98], ['1009', '2002', 12], ['1007', '2002', 99], ['1008', '2002', 39], ['1003', '2003', 34], ['1004', '2003', 43], ['1000', '2003', 25], ['1060', '2003', 60], ['1090', '2003', 88], ['1005', '2004', 81], ['1080', '2004', 59], ['1030', '2004', 87], ['1001', '2004', 35], ['1090', '2004', 33]]

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def get_func():
    if request.method == "GET":
        return render_template("index.html")
    elif request.method == "POST":
        ID = request.form["ID"]
        id_value = request.form["id_value"]
        if (ID == "course_id" and id_value not in c_ids) or (ID == "student_id" and id_value not in st_ids):
            return render_template("error.html")
        
        elif ID == "course_id" and id_value in c_ids:
            maxi, avg, marks = 0, 0, []
            for value in range(len(info)):
                if id_value == info[value][1]:
                    marks.append(info[value][2])
                    avg += info[value][2]
                    if info[value][2] > maxi:
                        maxi = info[value][2]
            avg = avg/len(info)
            plt.hist(marks)
            plt.xlabel("Marks")
            plt.ylabel("Frequency")
            plt.savefig("templates/hist.png")
            return render_template("Course_details.html", average_marks=avg, maximum_marks=maxi)
        
        elif ID == "student_id" and id_value in st_ids:
            data, total = [], 0
            for value in range(len(info)):
                if id_value == info[value][0]:
                    data.append({"student_id": info[value][0], "course_id": info[value][1], "marks": info[value][2]})
                    total += info[value][2]
            return render_template("Student_details.html", data=data, total=total)
            

if __name__ == "__main__":
    app.debug = True
    app.run()
