import React from 'react';

class SubmitFooter extends React.Component {
  render() {
    return (
      <div className="modal-footer">
        <a href={props.modalID}>
          <button type="submit" className="btn green uppercase">
            Submit
          </button>
        </a>
      </div>
    );
  }
}

export default SubmitFooter;
