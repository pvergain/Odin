import React from "react";

const DropdownButton = props => {
  return (
    <div className="btn-group">
      <button
        className="btn green uppercase dropdown-toggle"
        data-toggle="dropdown"
        data-delay="1000"
        data-close-others="true"
      >
        {props.children}
        <i className="fa fa-angle-down" />
      </button>
      <ul className="dropdown-menu" role="menu">
        {props.menuItems.map(item => {
          return (
            <li key={item.value}>
              <a href={item.url}>
                {item.value}
              </a>
            </li>
          );
        })}
      </ul>
    </div>
  );
};

export default DropdownButton;
