const headingsMapService = function () {
    const classPrefix = 'biohead';
    const headErrorClass = 'head-error';
    const headErrorH1Class = 'head-error-h1';
    const tooltipErrorClass = 'tooltip-error';
    const noHeadClass = 'no-headed';
    const headLevelsSpanElementClass = 'head-level';
    const additionalInfoClass = 'additional-info';
    const ariaLabelSpanClass = 'aria-label-span';
    const ariaLabelledBySpanClass = 'aria-labelled-span';
    const tooltipItemClass = 'tooltip-item';
    const noHeadingsText = 'No headings';
    const listClassPrefix = 'headingsMap-h';
    const listTag = 'ul';
    const itemTag = 'li';

    const defaultSettings = {
        showAriaHeaders: true,
        highLightElements: true
    };
    const a11ySettings = {
        showAriaHeaders: true,
        showAriaLabelContent: true,
        showHiddenHeaders: false,
        showHiddenContent: false,
        showAnchors: true,
        highLightElements: true
    };
    const HTMLSettings = {
        showAriaHeaders: false,
        showAriaLabelContent: false,
        showHiddenHeaders: true,
        showHiddenContent: true,
        showAnchors: true,
        highLightElements: true
    };

    const {
        createElement,
        createTextNode,
        getText,
        getAriaLabel,
        getAriaLabelByIdRelatedContent,
        isVisibleForA11y,
        getAnchorFromElement,
        anchorClass,
        anchorTitle,
        getHeadingInfo,
        dataElementIdAttrName,
        dataAnchorIdAttrName,
        getHeadings,
        getVisibilityClass
    } = utilsService();

    const {
        generateSectionForMap,
        removeAnchorFromHref
    } = commonFunctionalitiesService();

    return {
        headingsMap: headingsMapBackwardsCompatible,
        headingsMapA11y,
        headingsMapHTML
    };

    function headingsMapBackwardsCompatible(settings = {}) {
        const updatedSettings = Object.assign({}, settings, defaultSettings);
        return headingsMap(updatedSettings);
    }

    function headingsMapA11y(settings = {}) {
        const updatedSettings = Object.assign({}, settings, a11ySettings);
        return headingsMap(updatedSettings);
    }

    function headingsMapHTML(settings = {}) {
        const updatedSettings = Object.assign({}, settings, HTMLSettings);
        return headingsMap(updatedSettings);
    }

    function headingsMap(settings = {}) {
        return generateHeadingsMap;

        function generateHeadingsMap() {
            let previous = 0;
            let currentLevel = 0;
            const showAriaHeaders = settings.showAriaHeaders;
            const showHiddenHeaders = settings.showHiddenHeaders;
            const showAnchors = settings.showAnchors;
            const showTooltip = settings.showTooltip
            const getTextSettings = {
                showAriaLabelContent: settings.showAriaLabelContent,
                showHiddenContent: showHiddenHeaders
            };

            const headingsMapSection = generateSectionForMap();

            const documentToCheck = window.document;
            const headings = getHeadings(documentToCheck, settings);

            const locationHref = removeAnchorFromHref(window.location.href);

            let mainList = createElement(listTag, {'class': listClassPrefix + currentLevel});

            headingsMapSection.appendChild(mainList);

            let headingElementsLength = headings.length;
            if (!headingElementsLength) {
                let item = createElement(itemTag);
                mainList.appendChild(item);
                let noHeadingsTextNode = createTextNode(noHeadingsText);
                let noHeadingsSpanNode = createElement('span', {'class': noHeadClass});
                noHeadingsSpanNode.appendChild(noHeadingsTextNode);
                item.appendChild(noHeadingsSpanNode);

                return headingsMapSection;
            }

            for (let i = 0; i < headingElementsLength; i++) {
                const {header, isVisible} = headings[i];
                const headerId = header.getAttribute(dataElementIdAttrName);
                const headingInfo = getHeadingInfo(header, settings);
                const tagName = headingInfo.tagName.toLowerCase();
                const headingRole = headingInfo.headingRole;

                currentLevel = headingInfo.level;

                const item = createElement(itemTag);

                if (currentLevel > previous) {
                    let levelForClassValue = ((currentLevel === previous + 1) ? currentLevel : (previous + 1));
                    let classValue = listClassPrefix + levelForClassValue;
                    let descendantListElement = createElement(listTag, {'class': classValue});

                    descendantListElement.appendChild(item);

                    if (mainList.tagName.toLowerCase() === listTag) {
                        mainList.appendChild(item);
                    } else {
                        mainList.appendChild(descendantListElement);
                    }
                } else if (currentLevel === previous) {
                    mainList = mainList.parentNode;
                    mainList.appendChild(item);
                } else if (currentLevel < previous) {
                    let parentList = mainList;

                    while (parentList.parentNode.getAttribute('class') !== 'hroot') {
                        parentList = parentList.parentNode;
                        let parentListClass = parentList.getAttribute('class');

                        if (parentListClass.indexOf('h') >= 0) {
                            let cl = parseInt(parentListClass.replace(listClassPrefix, ''));
                            if (currentLevel >= cl) {
                                mainList = parentList;
                                break;
                            }
                        } else {
                            let precedingHeadLevel = parseInt(parentListClass.replace(classPrefix, ''));

                            if (currentLevel > precedingHeadLevel) {
                                mainList = parentList.getElementsByTagName(listTag)[0];
                                break;
                            } else if (currentLevel === precedingHeadLevel) {
                                mainList = parentList.parentNode;
                                break;
                            }
                        }
                    }
                    mainList.appendChild(item);
                }

                mainList = item;
                let level = currentLevel;

                const isElementVisibleFn = (element) => {
                    const showHiddenContent = getTextSettings.showHiddenContent;

                    return showHiddenContent || isVisibleForA11y(element);
                };

                const showAriaLabelContent = settings.showAriaLabelContent || false;

                let ariaLabelSpan;
                let ariaLabelledBySpan;
                let ariaLabel;
                let ariaLabelledBy;
                if (showAriaLabelContent) {
                    ariaLabel = getAriaLabel(header, isElementVisibleFn);
                    if (ariaLabel) {
                        ariaLabelSpan = createElement('span', {'class': ariaLabelSpanClass}, ' [aria-label="' + ariaLabel + '"]');
                    }

                    ariaLabelledBy = getAriaLabelByIdRelatedContent(header);
                    if (ariaLabelledBy) {
                        ariaLabelledBySpan = createElement('span', {'class': ariaLabelledBySpanClass}, ' [aria-labelledby="' + ariaLabelledBy + '"]');
                    }
                }

                const headerText = getText(header, isElementVisibleFn);
                const visibilityClass = getVisibilityClass(isVisible);
                const linkElementProperties = {
                    [dataElementIdAttrName]: headerId,
                    'class': visibilityClass,
                    'title': headerText
                };

                const headLevelsSpanElement = createElement('span', {'class': headLevelsSpanElementClass + ' ' + additionalInfoClass}, currentLevel);
                const headerTextNode = createTextNode(headerText);
                const linkChildNodes = [headLevelsSpanElement, headerTextNode];

                const sectionRef = getAnchorFromElement(header);
                if (sectionRef) {
                    if (showAnchors) {
                        const href = locationHref + '#' + sectionRef;
                        linkElementProperties.href = href;
                        const anchorElement = createElement('span', {
                            [dataAnchorIdAttrName]: href,
                            'class': anchorClass,
                            'title': anchorTitle
                        });
                        linkChildNodes.push(anchorElement);
                    }
                } else{
                    linkElementProperties.tabindex = '0';
                }

                const linkElement = createElement('a', linkElementProperties, linkChildNodes);

                if (ariaLabelSpan) {
                    linkElement.appendChild(ariaLabelSpan)
                }
                if (ariaLabelledBySpan) {
                    linkElement.appendChild(ariaLabelledBySpan)
                }

                mainList.appendChild(linkElement);
                mainList.classList.add(classPrefix + level);

                const emptyHeader = headerText.trim().length === 0;
                if (emptyHeader) {
                    linkElement.classList.add(headErrorClass);
                }

                const incorrectLevel = currentLevel > previous + 1;
                let missingH1 = false;
                if (incorrectLevel) {
                    missingH1 = i === 0;
                    linkElement.classList.add(missingH1 ? headErrorH1Class : headErrorClass);
                }
                previous = currentLevel;


                const tooltipContent = createElement('span', {
                    'class': 'tooltip-reference-content',
                    [dataElementIdAttrName]: headerId
                });

                const tooltipData = [{content: headerText}];

                if(ariaLabel) {
                    tooltipData.push({content: `aria-label: ${ariaLabel}`})
                }

                if(ariaLabelledBy) {
                    tooltipData.push({content: `aria-labelledby: ${ariaLabelledBy}`})
                }
                tooltipData.push({content: `Heading level: ${currentLevel}`})
                tooltipData.push({content: `Element: ${tagName}`})

                if(headingRole) {
                    tooltipData.push({content: `Role: ${headingRole}`})
                }

                if(emptyHeader){
                    tooltipData.push({content: ['Error', 'Empty header'], attributes: {class: tooltipErrorClass}});
                }
                if(incorrectLevel){
                    tooltipData.push({content: ['Error', missingH1 ? 'Missing H1' : 'Wrong level hierarchy'], attributes: {class: tooltipErrorClass}});
                }
                if(sectionRef){
                    tooltipData.push({content: `Click the anchor icon to copy the URL`, attributes: {class: anchorClass}});
                }
                if(!isVisible){
                    tooltipData.push({content: 'Potentially hidden', attributes: {class: visibilityClass}});
                }

                tooltipData.forEach((data) => {
                    const content = data.content;
                    const attributes = data.attributes || {};
                    let dataAttribute = '';
                    let dataValue;

                    if (typeof content === 'string' || content.nodeType) {
                        dataValue = content;
                    } else {
                        dataAttribute = createElement('strong', {}, `${content[0]}: `);
                        dataValue = content[1];
                    }
                    const tooltipDataItem = createElement('span', attributes, [dataAttribute, dataValue]);
                    tooltipDataItem.classList.add(tooltipItemClass);
                    tooltipContent.appendChild(tooltipDataItem);
                });
                linkElement.append(tooltipContent)
            }

            return headingsMapSection;
        }
    }
};