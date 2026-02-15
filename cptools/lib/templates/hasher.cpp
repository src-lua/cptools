#include <bits/stdc++.h>

using namespace std;

string getHash(string s){
	ofstream("z.cpp") << s;
	system("g++ -E -P -dD -fpreprocessed ./z.cpp | tr -d '[:space:]' | md5sum > sh");
	ifstream("sh") >> s;
	return s.substr(0, 3);
}

int main(){
	string l, t;
	stack<string> st({""});
	while(getline(cin, l)){
        t = l;
		for(auto c : l)
			if(c == '{') st.push(""); else
			if(c == '}') t = st.top()+l, st.pop();
		cout << getHash(t) + " " + l << endl;
		st.top() += t;
	}
}
