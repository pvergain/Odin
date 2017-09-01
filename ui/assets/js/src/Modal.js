import React from 'react';
import SubmitFooter from './SubmitFooter';

import CodeMirror from 'react-codemirror';
import 'codemirror/lib/codemirror.css';
import 'codemirror/theme/neat.css';
import 'codemirror/mode/python/python';

class Modal extends React.Component {
  constructor(props) {
    super(props);

    this.state = {code: ''};
    this.handleChange = this.handleChange.bind(this);
  }

  componentDidMount() {
    this.textInput.getCodeMirror().refresh();
  }

  handleChange(newCode) {
    this.setState({code: newCode});
  }

  render() {
    const {modalID, task} = this.props;
    const {code} = this.state;
    const options = {
      lineNumbers: true,
      matchBrackets: true,
      indentUnit: 4,
      theme: 'neat',
      mode: 'python',
    };

    return (
      <div
        id={`${modalID}`}
        className="modal fade"
        aria-hidden="true"
        style={{display: 'none'}}>
        <div className="modal-dialog">
          <div className="modal-content">
            <div className="modal-header">
              <h4 className="modal-title">{task.name}</h4>
            </div>
            <div className="modal-body">
              <form method="POST" action="">
                <CodeMirror
                  value={code}
                  onChange={this.handleChange}
                  options={options}
                  ref={input => {
                    this.textInput = input;
                  }}
                />
              </form>
            </div>
            <SubmitFooter />
          </div>
        </div>
      </div>
    );
  }
}

export default Modal;
