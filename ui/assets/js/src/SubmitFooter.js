import React from "react";

const SubmitFooter = props => {
  return (
    <div className="modal-footer">
      <button
        onClick={() => document.getElementById("submit_solution_form").submit()}
        type="submit"
        className="btn green uppercase"
      >
        Submit
      </button>
    </div>
  );
};

export default SubmitFooter;
