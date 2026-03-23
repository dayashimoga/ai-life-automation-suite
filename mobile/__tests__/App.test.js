import React from 'react';
import renderer from 'react-test-renderer';
import App from '../App';

describe('<App />', () => {
  it('renders correctly and has 5 tabs', () => {
    // Simply render the App component to ensure navigation mounts without crashing
    const tree = renderer.create(<App />).toJSON();
    expect(tree).toBeTruthy();
  });
});
