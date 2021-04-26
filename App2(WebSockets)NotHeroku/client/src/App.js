import { Component } from "react"
import './App.css';
import FileDownload from 'js-file-download';
import io from 'socket.io-client';

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      complexity: null,
      scrutiny: null,
      meanGrid: null,
      resultingImage: null,
      loading: false,
      filesArray: [],
      answersStorage: []
    };
    this.handleSubmit = this.handleSubmit.bind(this);
    this.handleClickDownload = this.handleClickDownload.bind(this);
    this.handleServer = this.handleServer.bind(this);
    this.socket = null;
  }

  componentWillMount() {
    this.socket = io('http://localhost:9000');
  }

  handleServer(event) {
    var names = [];
    for (let i = 0; i < this.state.filesArray.length; i++) {
      names.push(this.state.filesArray[i]['name']);
    }
    this.socket.emit('sending tables', {
      files: this.state.filesArray,
      names: names
    });
    this.socket.on('response', (message) => {
      console.log(message);
    })
    this.socket.on("Otvet", (masfile)=>{
      this.setState({
        answersStorage: masfile['files']
      });
    })
    event.preventDefault();
  }

  handleClickDownload(event, idx) {
    const blob = new Blob([this.state.answersStorage[idx]], {
      type:
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    })
    FileDownload(blob, 'response.xlsx');
    event.preventDefault();
  }

  handleSubmit(event) {
    var mas=[this.state.complexity, this.state.scrutiny, this.state.meanGrid];
    this.socket.emit("sending oil", {'names_of_files':mas});
    this.setState({
      loading: true
    });
    this.socket.on('Otvet oil', (kartinka) => {
      this.setState({
        loading: false,
        resultingImage: kartinka
      });
    });
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
        onSubmit={this.handleServer}
      >
        <input type="file" id="file" multiple onChange={(e) => this.setState({
          filesArray: e.target.files
        })} />
        <input type="submit" value="Submit"></input>
      </form>
      <div>
        {this.state.answersStorage.length != 0
        ?
        <div>
        <button onClick={(event) => this.handleClickDownload(event, 0)}>Download first</button>
        <button onClick={(event) => this.handleClickDownload(event, 1)}>Download second</button>
        </div>
        :
        <div></div>}
      </div>
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
