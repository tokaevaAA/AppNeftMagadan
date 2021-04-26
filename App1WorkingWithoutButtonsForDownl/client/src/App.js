import React, { Component } from "react"
import axios from 'axios';
import xlsx from 'node-xlsx';
import './App.css';
import FileDownload from 'js-file-download';

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      complexity: null,
      scrutiny: null,
      meanGrid: null,
      resultingImage: null,
      loading: false,
      filesArray: []
    };
    this.handleSubmit = this.handleSubmit.bind(this);
    this.handleSubmitAnother = this.handleSubmitAnother.bind(this);
  }

  handleSubmitAnother(event) {
    const data = new FormData()
    for (let i = 0; i < this.state.filesArray.length; i++) {
      data.append('file', this.state.filesArray[i]);
    }
    axios.post('http://localhost:9000/multiple', data)
      .then(res => {
          for (let i = 0; i < 1; i++) {
        //for (let i = 0; i < res.data.length; i++) {
          var buffer = xlsx.build([res.data[i][0]]);
          const blob = new Blob([buffer], {
            type:
              'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
          })
          FileDownload(blob, `response${i+1}.xlsx`);
        }
      })
    event.preventDefault();
  }

  handleSubmit(event) {
    const data = new FormData();
    data.append('file', this.state.complexity);
    data.append('file', this.state.scrutiny);
    data.append('file', this.state.meanGrid);
    this.setState({
      loading: true
    })
    axios.post("http://localhost:9000/neft", data)
      .then(res => {
        this.setState({
          loading: false,
          resultingImage: res.data
        });
      })
    event.preventDefault();
  }

  render() {
    return (
      <div className="App">
      <div>
        {this.state.resultingImage
        ?
        <img src={`data:image/png;base64,${this.state.resultingImage}`} />
        :
        this.state.loading
        ?
        <div><h1>Loading...</h1></div>
        :
        <div><h1>Please load wells complexity, scrutiny and mean grid</h1></div>
        }
      </div>
      <form
        className="uploader"
        encType="multipart/form-data"
        onSubmit={this.handleSubmitAnother}
      >
        <input type="file" id="file" multiple onChange={(e) => this.setState({
          filesArray: e.target.files
        })} />
        <input type="submit" value="Submit"></input>
      </form>
      <form onSubmit={this.handleSubmit}>
        <label>
          Complexity:
          <input type="file" onChange={(e) => this.setState({
            complexity: e.target.files[0]
          })} />
        </label>
        <br></br>
        <label>
          Scrutiny:
          <input type="file" onChange={(e) => this.setState({
            scrutiny: e.target.files[0]
          })} />
        </label>
        <br></br>
        <label>
          Mean grid:
          <input type="file" onChange={(e) => this.setState({
            meanGrid: e.target.files[0]
          })} />
        </label>
        <br></br>
        <input type="submit" value="Submit" />
      </form>
      </div>
    )
  }
}

export default App;
