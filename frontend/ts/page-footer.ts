import { preventDuplicateSubmit, preventDuplicateClick } from './utils/prevent_events';

(window as any).preventDuplicateSubmit = preventDuplicateSubmit;
(window as any).preventDuplicateClick = preventDuplicateClick;
